from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from ..services.deployment_service import deployment_service
from ..db.crud import crud
from ..db.models import Account

router = APIRouter()

class DeployRequest(BaseModel):
    user_id: str
    region: str = "us-east-1"

class AccountCreate(BaseModel):
    access_key: str
    secret_key: str
    regions: list[str] = ["us-east-1"]
    total_quota: int = 10

@router.post("/deploy")
async def deploy(request: DeployRequest):
    try:
        result = await deployment_service.deploy_instance(request.user_id, request.region)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/accounts")
async def add_account(account: AccountCreate):
    # Convert Pydantic model to DB model (mostly same fields)
    new_account = Account(
        access_key=account.access_key,
        secret_key=account.secret_key,
        regions=account.regions,
        remaining_quota=account.total_quota,
        total_quota=account.total_quota
    )
    # Insert manually using motor directly for now or add create_account to CRUD
    from ..db.mongodb import db
    result = await db.db.accounts.insert_one(new_account.model_dump(by_alias=True, exclude=["id"]))
    return {"status": "created", "id": str(result.inserted_id)}

@router.get("/status/{instance_id}")
async def get_status(instance_id: str):
    # Retrieve from DB
    from ..db.mongodb import db
    from bson import ObjectId
    doc = await db.db.instances.find_one({"_id": ObjectId(instance_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # In real world, we might trigger a live check here if it's still pending
    # But for now, just return DB state
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("/instances")
async def list_instances(user_id: str):
    instances = await crud.get_user_instances(user_id)
    return [inst.model_dump(by_alias=True) for inst in instances]
