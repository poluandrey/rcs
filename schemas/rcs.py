from typing import List, Optional

from pydantic import BaseModel


class RCSBatchCapabilityResponse(BaseModel):
    reachableUsers: Optional[List[str]] = None
    totalRandomSampleUserCount: Optional[int] = None
    reachableRandomSampleUserCount: Optional[int] = None
