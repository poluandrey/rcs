from typing import Optional

from pydantic import BaseModel

from RCS.google import schema as google_resp_schema
from RCS.google.schema import RCSBatchCapabilityResponse
from RCS.sinch import schema as sinch_resp_schema


class RCSCapabilityResponse(BaseModel):
    phone_number: str
    rcs_enable: bool
    country: Optional[str] = None
    raw_response: Optional[
        google_resp_schema.SuccessfulCapabilityResponse |
        google_resp_schema.FailedCapabilityResponse |
        sinch_resp_schema.SuccessfulCapableResponse |
        sinch_resp_schema.FailedCapabilityResponse |
        RCSBatchCapabilityResponse
        ] = None

# пока не получаетя сделать протокол из за того что клиенты по разному инициализируются
# class ApiClient(Protocol):
#
#     async def rcs_capable(self, phone_number: str, country='undefined') -> RCSCapabilityResponse:
#         pass
#
#     async def batch_capable(self, phone_numbers, country) -> AsyncIterator[List[RCSCapabilityResponse]]:
#         pass
