from .account_manager import account_manager
from .aws_service import AWSService
from ..db.crud import crud
from ..db.models import Instance, InstanceStatus, LogLevel, SystemLog
from botocore.exceptions import ClientError
import secrets
import string

class DeploymentService:
    async def deploy_instance(self, user_id: str, region: str = "us-east-1"):
        # 1. Get Account
        account = await account_manager.get_available_account(region)
        if not account:
            raise Exception("No available accounts found")

        # 2. Prepare AWS Service
        aws = AWSService(account.access_key, account.secret_key, region)
        
        # 3. Generate Password & UserData
        password = self._generate_password()
        user_data = aws.generate_user_data(password)
        
        # 4. Launch Instance
        # Hardcoded AMI and Type for demo. In production, these should be config/params.
        # AMI for Ubuntu 22.04 in us-east-1 (example)
        ami_id = "ami-0c7217cdde317cfec" 
        instance_type = "t2.micro"

        try:
            instance_aws_id = aws.run_instance(ami_id, instance_type, user_data)
        except ClientError as e:
            # Handle Auth Failure -> Mark Account Dead
            if e.response['Error']['Code'] == 'AuthFailure':
                await account_manager.mark_account_dead(str(account.id), str(e))
                # Retry logic should be here (recursive call or loop)
                # For now, just raise
                raise Exception("Account authentication failed. Please try again.")
            raise e

        # 5. Record in DB
        instance_model = Instance(
            instance_id=instance_aws_id,
            account_id=str(account.id),
            region=region,
            user_id=user_id,
            initial_password=password,
            status=InstanceStatus.PENDING
        )
        db_id = await crud.create_instance(instance_model)
        
        # 6. Decrement Quota
        await crud.decrement_account_quota(str(account.id))

        return {
            "db_id": db_id,
            "instance_id": instance_aws_id,
            "account_id": str(account.id)
        }

    async def check_and_update_status(self, instance_db_id: str):
        # Retrieve from DB to get Account credentials
        # This is a bit complex because we need the account credentials again.
        # In a real app, we might store credentials encrypted or just link to the Account document.
        # Let's assume we can fetch the instance and then the account.
        pass # To be implemented if needed for sync polling
        
    def _generate_password(self, length=12):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(length))

deployment_service = DeploymentService()
