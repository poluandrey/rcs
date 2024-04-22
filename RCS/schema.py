from typing import Optional

from pydantic import BaseModel

from RCS.google import schema as google_resp_schema
from RCS.sinch import schema as sinch_resp_schema


class RCSCapabilityResponse(BaseModel):
    msisdn: str
    rcs_enable: bool
    country: str
    raw_response: Optional[
        google_resp_schema.SuccessfulCapabilityResponse |
        google_resp_schema.FailedCapabilityResponse |
        sinch_resp_schema.SuccessfulCapableResponse |
        sinch_resp_schema.FailedCapabilityResponse
        ] = None
