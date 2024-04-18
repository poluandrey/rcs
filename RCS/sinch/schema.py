from typing import List
from enum import Enum, auto

from pydantic import BaseModel


class MAAPCapabilitiesItem(Enum):
    chat = auto()
    fileTransfer = auto()
    videoCall = auto()
    geolocationPush = auto()
    callComposer = auto()
    chatBotCommunication = auto()


class RcsCapableResponse(BaseModel):
    rcs_enabled: bool
    at: str
    msisdn: str
    mcc: str
    mnc: str
    capabilities: List[MAAPCapabilitiesItem]


class RcsErrorResponse(BaseModel):
    error: str