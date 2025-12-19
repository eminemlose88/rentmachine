from ..db.crud import crud
from ..db.models import InstanceStatus
from .aws_service import AWSService
from .account_manager import account_manager
from ..db.mongodb import db
import asyncio
from bson import ObjectId
from datetime import datetime

class MonitorService:
    async def check_pending_instances(self):
        """
        Polls PENDING instances and updates their status if IP is assigned.
        """
        cursor = db.db.instances.find({"status": InstanceStatus.PENDING})
        pending_instances = await cursor.to_list(length=100)

        for inst_doc in pending_instances:
            inst_id = inst_doc["_id"]
            aws_inst_id = inst_doc["instance_id"]
            account_id = inst_doc["account_id"]
            region = inst_doc["region"]

            account = await crud.get_account_by_id(account_id)
            if not account:
                print(f"Account {account_id} not found for instance {aws_inst_id}")
                continue

            try:
                aws = AWSService(account.access_key, account.secret_key, region)
                info = aws.get_instance_info(aws_inst_id)
                
                state = info.get("state")
                public_ip = info.get("public_ip")
                
                if state == "running" and public_ip:
                    print(f"Instance {aws_inst_id} is running with IP {public_ip}")
                    await crud.update_instance_info(inst_id, public_ip, InstanceStatus.RUNNING)
                elif state == "terminated":
                     await crud.update_instance_info(inst_id, None, InstanceStatus.TERMINATED)
            except Exception as e:
                print(f"Error checking instance {aws_inst_id}: {e}")

    async def auto_replenish(self):
        """
        Phase 3.1: Check for instances that should be running but are terminated.
        """
        from .deployment_service import deployment_service
        
        # Find instances that are TERMINATED but have future expire_at (valid subscription)
        # and haven't been replenished yet.
        cursor = db.db.instances.find({
            "status": InstanceStatus.TERMINATED,
            "expire_at": {"$gt": datetime.utcnow()},
            "metadata.replenished": {"$ne": True}
        })
        dead_instances = await cursor.to_list(length=100)

        for inst in dead_instances:
            print(f"Replenishing instance {inst['instance_id']}")
            try:
                user_id = inst['user_id']
                region = inst['region']
                original_expire_at = inst['expire_at']
                
                # Deploy new instance
                result = await deployment_service.deploy_instance(user_id, region)
                new_db_id = result['db_id']
                
                # Update new instance with original expiration
                await db.db.instances.update_one(
                    {"_id": ObjectId(new_db_id)},
                    {"$set": {"expire_at": original_expire_at}}
                )
                
                # Mark old instance as replenished
                await db.db.instances.update_one(
                    {"_id": inst["_id"]},
                    {"$set": {"metadata.replenished": True, "metadata.replaced_by": new_db_id}}
                )
                
            except Exception as e:
                print(f"Failed to replenish {inst['instance_id']}: {e}")

monitor_service = MonitorService()
