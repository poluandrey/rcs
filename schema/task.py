from typing import Optional

from pydantic import UUID4, BaseModel


class BaseTask(BaseModel):
    id: int
    name: UUID4

    class Config:
        orm_model = True
        from_attributes = True


class BaseTaskResult(BaseModel):
    task: int
    country: str
    msisdn: Optional[str] = None
