from typing import Optional
from helpers import _post, PorkbunError

PINGURI = "https://api.porkbun.com/api/json/v3/ping"
V4ONLYPINGURI = "https://api-ipv4.porkbun.com/api/json/v3/ping"

NSUPDATEURI = "https://api.porkbun.com/api/json/v3/domain/updateNS/{domain}"

CREATEURI = "https://api.porkbun.com/api/json/v3/dns/create/{domain}"

READURI = "https://api.porkbun.com/api/json/v3/dns/retrieveByNameType/{domain}/{type}/{subdomain}"

UPDATEURI = "https://api.porkbun.com/api/json/v3/dns/editByNameType/{domain}/{type}/{subdomain}"

DELETEURI = "https://api.porkbun.com/api/json/v3/dns/deleteByNameType/{domain}/{type}/{subdomain}"

ALLOWEDTYPES = ["A", "MX", "CNAME", "ALIAS", "TXT", "NS", "AAAA", "SRV", "TLSA", "CAA"]

ALLOWEDTYPES_PRIO = ["SRV", "MX"]

def nsupdate(domain:str, nslist:list):
    payload = {"ns": nslist}
    nsurequest = _post(NSUPDATEURI.format(domain = domain), body = payload)

def create(domain:str, rtype:str, content:str, subdomain:str = "", ttl:int = 600, priority: Optional[int] = None):
    if rtype not in ALLOWEDTYPES:
        raise PorkbunError(f"Type {rtype} is not a valid record type supported by Porkbun")
    payload = {"type": rtype, "name": subdomain, "ttl": ttl, "content": content}
    if priority:
        if rtype not in ALLOWEDTYPES_PRIO:
            raise PorkbunError(f"Your request type {rtype} does not support priority")
        payload["prio"] = priority
    crequest = _post(CREATEURI.format(domain = domain), body = payload)

def read(domain:str, rtype:str, subdomain:str = ""):
    if rtype not in ALLOWEDTYPES:
        raise PorkbunError(f"Type {rtype} is not a valid record type supported by Porkbun")
    rrequest = _post(READURI.format(domain = domain, type = rtype, subdomain = subdomain))
    return rrequest.json()["records"]

def update(domain:str, rtype:str, content:str, subdomain:str = "", ttl:int = 600, priority: Optional[int] = None):
    if rtype not in ALLOWEDTYPES:
        raise PorkbunError(f"Type {rtype} is not a valid record type supported by Porkbun")
    payload = {"content": content, "ttl": ttl}
    if priority:
        if rtype not in ALLOWEDTYPES_PRIO:
            raise PorkbunError(f"Your request type {rtype} does not support priority")
        payload["prio"] = priority
    urequest = _post(UPDATEURI.format(domain = domain, type = rtype, subdomain = subdomain), body = payload)

def delete(domain:str, rtype:str, subdomain:str = ""):
    if rtype not in ALLOWEDTYPES:
        raise PorkbunError(f"Type {rtype} is not a valid record type supported by Porkbun")
    drequest = _post(DELETEURI.format(domain = domain, type = rtype, subdomain = subdomain))

#def ddns_update(domain:str, ip:str = "", subdomain:str = "", ipv4only:bool = True):
#    if ip:
#        ipaddr = ip
#    else:
#        ipaddr = ping(apikey = apikey, secretapikey = secretapikey, ipv4only = False if not ipv4only else True)
#    update(domain, "A" if ipv4only or ":" not in ip else "AAAA", subdomain = subdomain, content = ipaddr, apikey = apikey, secretapikey = secretapikey)
