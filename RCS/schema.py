from typing import List, Optional

from pydantic import BaseModel


class RCSBatchCapabilityResponse(BaseModel):
    reachableUsers: Optional[List[str]] = None
    totalRandomSampleUserCount: Optional[int] = None
    reachableRandomSampleUserCount: Optional[int] = None


class RCSDataForCheck(BaseModel):
    country: str
    msisdns: List[str]


class RCSBatchCapabilityTask(BaseModel):
    task_id: str
    data: List[RCSDataForCheck]
