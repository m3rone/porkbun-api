from .helpers import _get, _post, PorkbunError
from typing import TypedDict, Literal, NotRequired

INVITEURI = "https://api.porkbun.com/api/json/v3/account/invite"
INVITESTATUSURI = "https://api.porkbun.com/api/json/v3/account/inviteStatus/{token}"
BALANCEURI = "https://api.porkbun.com/api/json/v3/account/balance"
APISETTINGSURI = "https://api.porkbun.com/api/json/v3/account/apiSettings"

class _Invite(TypedDict):
    status: str
    inviteToken: str
    inviteUrl: str
    expires: str

def invite(email:str = "", returnUrl = ""):
    data = {"email": email, "returnUrl": returnUrl}
    inviteReq:_Invite = _post(INVITEURI, data)
    return inviteReq

class _InviteStatus(TypedDict):
    status: str
    inviteStatus: Literal["PENDING", "ACCEPTED", "EXPIRED"]
    newAccountId: NotRequired[int]

def inviteStatus(token:str):
    inviteStatQueryReq:_InviteStatus = _get(INVITESTATUSURI.format(token = token))
    return inviteStatQueryReq

class _Balance(TypedDict):
    status: str
    balance: int
    display: str

def balance():
    balanceReq:_Balance = _get(BALANCEURI)
    return balanceReq

class _ApiSettingsSettings(TypedDict):
    monthlySpendLimit: int | None
    lowBalanceAlert: int | None
    autoTopup: bool
    topupThreshold: int | None
    topupAmount: int | None

class _ApiSettings(TypedDict):
    status: str
    settings: _ApiSettingsSettings
    monthlySpend: int

def apiSettings():
    apiSettingsReq:_ApiSettings = _get(APISETTINGSURI)
    return apiSettingsReq

