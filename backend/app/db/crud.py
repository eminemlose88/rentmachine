    async def update_instance_info(self, instance_db_id: str, public_ip: str, status: InstanceStatus):
        await db.db.instances.update_one(
            {"_id": ObjectId(instance_db_id)},
            {"$set": {"public_ip": public_ip, "status": status}}
        )
    
    async def get_user_instances(self, user_id: str) -> List[Instance]:
        cursor = db.db.instances.find({"user_id": user_id})
        instances = await cursor.to_list(length=100)
        return [Instance(**inst) for inst in instances]

    async def log_event(self, log: SystemLog):
