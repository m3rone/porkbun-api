from helpers import _post, _get, PorkbunError

def ping(apikey:str = "", secretapikey:str = "", ipv4only:bool = True):
    pingrequest = _post(url=V4ONLYPINGURI if ipv4only else PINGURI)
    return pingrequest["yourIp"]
