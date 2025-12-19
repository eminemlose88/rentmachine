from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional, Annotated
from datetime import datetime
from enum import Enum

# Helper for MongoDB _id
PyObjectId = Annotated[str, BeforeValidator(str)]

class AccountStatus(str, Enum):
    ACTIVE = "active"
    DEAD = "dead"
    SUSPENDED = "suspended"

class Account(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    access_key: str
    secret_key: str
    regions: List[str] = ["us-east-1"]
    status: AccountStatus = AccountStatus.ACTIVE
    remaining_quota: int = 10
    total_quota: int = 10
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InstanceStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"

class Instance(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    instance_id: str
    account_id: str  # Reference to Account ID
    region: str
    user_id: str
    public_ip: Optional[str] = None
    initial_password: Optional[str] = None
    status: InstanceStatus = InstanceStatus.PENDING
    launch_time: datetime = Field(default_factory=datetime.utcnow)
    expire_at: Optional[datetime] = None
    metadata: dict = Field(default_factory=dict)
    
class LogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class SystemLog(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: LogLevel = LogLevel.INFO
    message: str
    metadata: Optional[dict] = None
