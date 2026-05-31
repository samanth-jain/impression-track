from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId


class ImpressionBase(BaseModel):
    page_url: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    metadata: Optional[dict] = None


class ImpressionCreate(ImpressionBase):
    pass


class ImpressionResponse(ImpressionBase):
    id: str = Field(alias="_id")
    timestamp: datetime
    
    class Config:
        populate_by_name = True
