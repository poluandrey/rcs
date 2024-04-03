from pydantic import BaseModel, UUID4


class BaseTask(BaseModel):
    id: int
    name: UUID4

    class Config:
        orm_model = True
        from_attributes = True
