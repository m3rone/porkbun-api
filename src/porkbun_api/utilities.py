from .helpers import _post

PINGURI = "https://api.porkbun.com/api/json/v3/ping"
V4ONLYPINGURI = "https://api-ipv4.porkbun.com/api/json/v3/ping"

def ping(ipv4only:bool = True):
    pingrequest = _post(url=V4ONLYPINGURI if ipv4only else PINGURI)
    return pingrequest["yourIp"]
