import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple
import time
import base64

class AWSService:
    def __init__(self, access_key: str, secret_key: str, region: str):
        self.client = boto3.client(
            'ec2',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        self.resource = boto3.resource(
            'ec2',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

    def run_instance(self, image_id: str, instance_type: str, user_data: str) -> Optional[str]:
        """
        Launches an EC2 instance. Returns the Instance ID.
        """
        try:
            response = self.client.run_instances(
                ImageId=image_id,
                InstanceType=instance_type,
                MinCount=1,
                MaxCount=1,
                UserData=user_data,
                # NetworkInterfaces=[{
                #     'DeviceIndex': 0,
                #     'AssociatePublicIpAddress': True
                # }]
                # Usually default VPC handles this, or need to specify subnet. 
                # For simplicity, assuming default VPC with auto-assign public IP.
            )
            instance_id = response['Instances'][0]['InstanceId']
            return instance_id
        except ClientError as e:
            print(f"Error launching instance: {e}")
            raise e

    def get_instance_info(self, instance_id: str) -> dict:
        """
        Returns instance info including Public IP and State.
        """
        try:
            response = self.client.describe_instances(InstanceIds=[instance_id])
            reservations = response.get('Reservations', [])
            if not reservations:
                return {}
            
            instance = reservations[0]['Instances'][0]
            return {
                'state': instance['State']['Name'],
                'public_ip': instance.get('PublicIpAddress'),
                'launch_time': instance.get('LaunchTime')
            }
        except ClientError as e:
            print(f"Error describing instance: {e}")
            raise e

    def terminate_instance(self, instance_id: str):
        try:
            self.client.terminate_instances(InstanceIds=[instance_id])
        except ClientError as e:
            print(f"Error terminating instance: {e}")
            raise e

    @staticmethod
    def generate_user_data(password: str) -> str:
        """
        Generates UserData script to set root password and enable SSH password auth.
        """
        script = f"""#!/bin/bash
echo "root:{password}" | chpasswd
sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^#PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
systemctl restart sshd
        """
        return script
