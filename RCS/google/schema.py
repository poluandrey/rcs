from typing import Dict, List, Optional

from pydantic import BaseModel


class SuccessfulCapabilityResponse(BaseModel):
    features: List[str]


class FailedCapabilityResponse(BaseModel):
    error: Dict[str, str | int]


class RCSBatchCapabilityResponse(BaseModel):
    reachableUsers: Optional[List[str]] = None
    totalRandomSampleUserCount: Optional[int] = None
    reachableRandomSampleUserCount: Optional[int] = None


class RCSDataForCheck(BaseModel):
    country: str
    msisdns: List[str]


class RCSBatchCapabilityTask(BaseModel):
    task_id: int
    data: List[RCSDataForCheck]
