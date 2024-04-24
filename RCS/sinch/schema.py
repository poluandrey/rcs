from enum import Enum, auto
from typing import List

from pydantic import BaseModel


class MAAPCapabilitiesItem(Enum):
    chat = auto()
    fileTransfer = auto()
    videoCall = auto()
    geolocationPush = auto()
    callComposer = auto()
    chatBotCommunication = auto()


class SuccessfulCapableResponse(BaseModel):
    rcs_enabled: bool
    at: str
    msisdn: str
    mcc: str
    mnc: str
    capabilities: List[MAAPCapabilitiesItem]


class FailedCapabilityResponse(BaseModel):
    error: str
