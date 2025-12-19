from .mongodb import db
from .models import Account, AccountStatus, Instance, InstanceStatus, SystemLog
from typing import Optional, List
from bson import ObjectId

class CRUD:
    async def get_active_accounts(self) -> List[Account]:
        cursor = db.db.accounts.find({"status": AccountStatus.ACTIVE, "remaining_quota": {"$gt": 0}})
        accounts = await cursor.to_list(length=100)
        return [Account(**acc) for acc in accounts]

    async def get_account_by_id(self, account_id: str) -> Optional[Account]:
        doc = await db.db.accounts.find_one({"_id": ObjectId(account_id)})
        if doc:
            return Account(**doc)
        return None

    async def update_account_status(self, account_id: str, status: AccountStatus):
        await db.db.accounts.update_one(
            {"_id": ObjectId(account_id)},
            {"$set": {"status": status}}
        )

    async def decrement_account_quota(self, account_id: str):
        await db.db.accounts.update_one(
            {"_id": ObjectId(account_id)},
            {"$inc": {"remaining_quota": -1}}
        )

    async def create_instance(self, instance: Instance):
        instance_dict = instance.model_dump(by_alias=True, exclude=["id"])
        result = await db.db.instances.insert_one(instance_dict)
        return str(result.inserted_id)

    async def update_instance_info(self, instance_db_id: str, public_ip: str, status: InstanceStatus):
        await db.db.instances.update_one(
            {"_id": ObjectId(instance_db_id)},
            {"$set": {"public_ip": public_ip, "status": status}}
        )
    
    async def log_event(self, log: SystemLog):
        log_dict = log.model_dump(by_alias=True, exclude=["id"])
        await db.db.logs.insert_one(log_dict)

crud = CRUD()
