import requests as req
from typing import Optional, Literal
from os import getenv
from json import loads as jloads
import response_dicts as resp_dict

APIKEY = ""
SECRETAPIKEY = ""

PINGURI = "https://api.porkbun.com/api/json/v3/ping"
V4ONLYPINGURI = "https://api-ipv4.porkbun.com/api/json/v3/ping"

NSUPDATEURI = "https://api.porkbun.com/api/json/v3/domain/updateNS/{domain}"

CREATEURI = "https://api.porkbun.com/api/json/v3/dns/create/{domain}"

READURI = "https://api.porkbun.com/api/json/v3/dns/retrieveByNameType/{domain}/{type}/{subdomain}"

UPDATEURI = "https://api.porkbun.com/api/json/v3/dns/editByNameType/{domain}/{type}/{subdomain}"

DELETEURI = "https://api.porkbun.com/api/json/v3/dns/deleteByNameType/{domain}/{type}/{subdomain}"

ALLOWEDTYPES = Literal["A", "MX", "CNAME", "ALIAS", "TXT", "NS", "AAAA", "SRV", "TLSA", "CAA"]

FORWARDTYPES = Literal["temporary", "permament"]

ALLOWEDTYPES_PRIO = ["SRV", "MX"]

## internal functions
def checkError(request):
    if request.json()["status"] == "ERROR":
        message = request.json()["message"]
        return message

class PorkbunError(Exception):
    ...

def defaultKeysIfNone(api, secret):
    keylist = (api, secret)
    if all(envkeys := (getenv("PORKBUN_APIKEY", ""), getenv("PORKBUN_SECRETAPIKEY", ""))): # defaults set to "" because pyright cant comprehend that all() checking whether both env vars exist
        return envkeys
    elif not any(keylist):
        return (APIKEY, SECRETAPIKEY)
    elif all(keylist):
        return keylist
    return ("", "")
##

def ping(apikey:str = "", secretapikey:str = "", ipv4only:bool = True):
    apikey, secretapikey = defaultKeysIfNone(apikey, secretapikey)
    payload = {"secretapikey" : secretapikey, "apikey" : apikey}
    pingrequest = req.post(V4ONLYPINGURI if ipv4only else PINGURI, json = payload)
    pingrequest.raise_for_status()
    if msg := checkError(pingrequest):
        raise PorkbunError(msg)
    return pingrequest.json()["yourIp"]

def nsupdate(domain:str, nslist:list, apikey:str = "", secretapikey:str = ""):
    apikey, secretapikey = defaultKeysIfNone(apikey, secretapikey)
    payload = {"secretapikey" : secretapikey, "apikey" : apikey, "ns": nslist}
    nsurequest = req.post(NSUPDATEURI.format(domain = domain), json = payload)
    nsurequest.raise_for_status()
    if msg := checkError(nsurequest):
        raise PorkbunError(msg)

def create(domain:str, rtype:str, content:str, apikey:str = "", secretapikey:str = "", subdomain:str = "",  ttl:int = 600, priority: Optional[int] = None):
    if rtype not in ALLOWEDTYPES:
        raise PorkbunError(f"Type {rtype} is not a valid record type supported by Porkbun")
    apikey, secretapikey = defaultKeysIfNone(apikey, secretapikey)
    payload = {"secretapikey": secretapikey, "apikey": apikey, "type": rtype, "name": subdomain, "ttl": ttl, "content": content}
    if priority:
        if rtype not in ALLOWEDTYPES_PRIO:
            raise PorkbunError(f"Your request type {rtype} does not support priority")
        payload["prio"] = priority
    crequest = req.post(CREATEURI.format(domain = domain), json = payload)
    crequest.raise_for_status()
    if msg := checkError(crequest):
        raise PorkbunError(msg)

def read(domain:str, rtype:str, subdomain:str = "", apikey:str = "", secretapikey:str = ""):
    if rtype not in ALLOWEDTYPES:
        raise PorkbunError(f"Type {rtype} is not a valid record type supported by Porkbun")
    apikey, secretapikey = defaultKeysIfNone(apikey, secretapikey)
    payload = {"secretapikey" : secretapikey, "apikey" : apikey}
    rrequest = req.post(READURI.format(domain = domain, type = rtype, subdomain = subdomain), json = payload)
    rrequest.raise_for_status()
    if msg := checkError(rrequest):
        raise PorkbunError(msg)
    return rrequest.json()["records"]

def update(domain:str, rtype:str, content:str, subdomain:str = "", apikey:str = "", secretapikey:str = "", ttl:int = 600, priority: Optional[int] = None):
    if rtype not in ALLOWEDTYPES:
        raise PorkbunError(f"Type {rtype} is not a valid record type supported by Porkbun")
    apikey, secretapikey = defaultKeysIfNone(apikey, secretapikey)
    payload = {"secretapikey": secretapikey, "apikey": apikey, "content": content, "ttl": ttl}
    if priority:
        if rtype not in ALLOWEDTYPES_PRIO:
            raise PorkbunError(f"Your request type {rtype} does not support priority")
        payload["prio"] = priority
    urequest = req.post(UPDATEURI.format(domain = domain, type = rtype, subdomain = subdomain), json = payload)
    urequest.raise_for_status()
    if msg := checkError(urequest):
        raise PorkbunError(msg)

def delete(domain:str, rtype:str, subdomain:str = "", apikey:str = "", secretapikey:str = ""):
    if rtype not in ALLOWEDTYPES:
        raise PorkbunError(f"Type {rtype} is not a valid record type supported by Porkbun")
    apikey, secretapikey = defaultKeysIfNone(apikey, secretapikey)
    payload = {"secretapikey" : secretapikey, "apikey" : apikey}
    drequest = req.post(DELETEURI.format(domain = domain, type = rtype, subdomain = subdomain), json = payload)
    drequest.raise_for_status()
    if msg := checkError(drequest):
        raise PorkbunError(msg)

def ddns_update(domain:str, ip:str = "", subdomain:str = "", apikey:str = "", secretapikey:str = "", ipv4only:bool = True):
    apikey, secretapikey = defaultKeysIfNone(apikey, secretapikey)
    if ip:
        ipaddr = ip
    else:
        ipaddr = ping(apikey = apikey, secretapikey = secretapikey, ipv4only = False if not ipv4only else True)
    update(domain, "A" if ipv4only or ":" not in ip else "AAAA", subdomain = subdomain, content = ipaddr, apikey = apikey, secretapikey = secretapikey)


class _MethodsHelper: # This will run all the calls, handle errors, etd.
    def __init__(self, apikey:str, secretapikey:str): #TODO docstring
        self.base_url = "https://api.porkbun.com/api/json/v3/"
        self.key = apikey
        self.secret = secretapikey
        self.auth = {
	    "secretapikey": secretapikey,
	    "apikey": apikey,
        }
        self.session = req.Session()
    
    def _requester(self, url:str, params:Optional[dict]={}):
        
        
        data = {**self.auth} # Merge auth and any passed json variables
        for k, v in params.items():
            if v == None: # Ignore blank params to avoid issues
                continue
            else:
                data[k] = v 
                
        
        method="post" # Some urls use get I guess
        get_method_urls = ["ping"]
        
        for murl in get_method_urls:
            if murl in url:
                method="get"
                break
       
        resp = self.session.request(method=method, url=self.base_url+url, json=data)
        
        if resp.status_code == 200:
            resp_content = jloads(resp.content)
            if 'status' in resp_content and resp_content['status'] != 'SUCCESS':
                raise Exception(resp) # TODO ADD ERROR HERE
            else:
                return resp_content
        
        elif resp.status_code == 400:
            raise Exception(resp.content) # TODO HANDLE THIS BETTER
        
        else:
            resp.raise_for_status()
    
    
class Porkbun:
    """Porkbun API Methods"""
    def __init__(self, apikey:str, secretapikey:str):
        """Get data from the Porkbun API

        Args:
            apikey (str): Your API Key
            secretapikey (str): Your Secret API Key 
        """
        
        # Inititiate the "subclasses".  They're not really subclasses but IDK what else to call them
        self._mh = _MethodsHelper(apikey, secretapikey)
        self.domain = _DomainMethods(self._mh)
        self.dns = _DNSMethods(self._mh)
        self.dnssec = _DNSSECMethods(self._mh)
        self.ssl = _SSLMethods(self._mh)
    
    def ping(self): # Requires auth
        url = "ping"
        resp = self._mh._requester(url)
        return resp_dict.Ping.from_json(resp)
    

class _DomainMethods(_MethodsHelper):
    """Domain API Methods"""
    def __init__(self, method_helper: _MethodsHelper):
        self._mh = method_helper
        self.url = "domain/"
    
    def get_pricing(self): #TODO DOES NOT WORK #TODO allow to run without auth
        url = "/pricing/get"
        resp = self._mh._requester(url)
        return resp['pricing']
    
    def list_all(self, start:Optional[int]=None, include_labels:bool=False):
        url = self.url+ "listAll"
        params = {
            "start": start,
            "includeLabels": include_labels
        }
        resp = self._mh._requester(url, params=params)
        return resp['domains']
    
    def check_availability(self, domain:str): # TODO could also be called "check" to match documentation
        url = self.url+ f"checkDomain/{domain}"
        resp = self._mh._requester(url)
        return resp
    
    def get_nameservers(self, domain:str):
        url = self.url+ f"getNs/{domain}"
        resp = self._mh._requester(url)
        return resp
    
    def update_nameservers(self, domain:str, nameservers:list):
        url = self.url+ f"updateNs/{domain}"
        params = {"ns": nameservers}
        resp = self._mh._requester(url, params)
        return resp
    
    def get_url_forwarding(self, domain:str):
        url = self.url+ f"getUrlForwarding/{domain}"
        resp = self._mh._requester(url)
        return resp["forwards"]
    
    def add_url_forwarding(self, domain:str, location:str, forward_type:FORWARDTYPES, include_path:bool, also_forward_subdomains:bool, subdomain:Optional[str]=None):
        url = self.url+ f"addUrlForward/{domain}"
        params = {
            "subdomain": subdomain,
            "location": location,
            "type": forward_type,
            "includePath": "yes" if include_path else "no",
            "wildcard": "yes" if also_forward_subdomains else "no",
        }
        resp = self._mh._requester(url, params=params)
        return resp #TODO this shouldn't return anything
    
    def delete_url_forwarding(self, domain:str, record_id:str|int):
        url = self.url+ f"deleteUrlForward/{domain}/{record_id}"
        resp = self._mh._requester(url)
        return resp #TODO this shouldn't return anything
    
    def get_glue_records(self, domain:str):
        url = self.url+ f"getGlue/{domain}"
        resp = self._mh._requester(url)
        return resp["hosts"]
    
    def add_glue_record(self, domain:str, subdomain:str, ips:list):
        url = self.url+ f"createGlue/{domain}/{subdomain}"
        params = {"ips": ips}
        resp = self._mh._requester(url, params=params)
        return resp #TODO this shouldn't return anything
    
    def update_glue_record(self, domain:str, subdomain:str, ips:list):
        url = self.url+ f"updateGlue/{domain}/{subdomain}"
        params = {"ips": ips}
        resp = self._mh._requester(url, params=params)
        return resp #TODO this shouldn't return anything
    
    def delete_glue_record(self, domain:str, subdomain:str):
        url = self.url+ f"deleteGlue/{domain}/{subdomain}"
        resp = self._mh._requester(url)
        return resp #TODO this shouldn't return anything
    

class _DNSMethods:
    """DNS API Methods"""
    def __init__(self, method_helper: _MethodsHelper):
        self._mh = method_helper
        self.url = "dns/"
        
    def get_record(self, domain:str, subdomain:Optional[str]=None, record_type:Optional[str]=None, record_id:Optional[int|str]=None):
        if record_id == None and (subdomain == None or record_type == None):
            raise ValueError("Must provide a record ID or subdomain and record type")
        
        if record_id != None:
            url = self.url+ f"/retrieve/{domain}/{record_id}"
        else:
            url = self.url+ f"retrieveByNameType/{domain}/{record_type}/{subdomain}"
        resp = self._mh._requester(url)
        return resp["records"]
    
    def add_record(self, domain:str, content:str, record_type:str, name:Optional[str]=None, ttl:Optional[int]=None, priority:Optional[int]=None, notes:Optional[str]=None): #TODO could also be "create_record" to match documentation
        url = self.url+ f"create/{domain}"
        params = {
            "name": name,
            "type": record_type,
            "content": content,
            "ttl": ttl,
            "prio": priority,
            "notes": notes
        }
        resp = self._mh._requester(url, params=params)
        return resp # Returns the ID
    
    def update_record(self, domain:str, content:str, record_id:Optional[int|str], name:Optional[str]=None, record_type:Optional[ALLOWEDTYPES]=None, ttl:Optional[int]=None, priority:Optional[int]=None, notes:Optional[str]=None):
        url = self.url+ f"edit/{domain}/{record_id}"
        # if name is not provided it'll wipe it out, will need to test the others
        if name == None or ttl == None or priority == None or notes == None or record_type == None: # Get the current record information to fill in
            record = self.get_record(domain=domain, record_id=record_id)
        
        params = {
            "name": name if name != None else record['name'],
            "type": record_type if record_type != None else record['type'],
            "content": content,
            "ttl": ttl if ttl != None else record['ttl'],
            "prio": priority if priority != None else record['prio'],
            "notes": notes if notes != None else record['notes']
            }
        
        resp = self._mh._requester(url, params=params)
        return resp # Returns nothing
        
    def delete_record(self, domain:str, subdomain:Optional[str]=None, record_type:Optional[str]=None, record_id:Optional[int|str]=None):
        if record_id == None and (subdomain == None or record_type == None):
            raise ValueError("Must provide a record ID or subdomain and record type")
        
        if record_id != None:
            url = self.url+ f"/delete/{domain}/{record_id}"
        else:
            url = self.url+ f"deleteByNameType/{domain}/{record_type}/{subdomain}"
        resp = self._mh._requester(url) # Returns nothing
    
class _DNSSECMethods:
    """DNSSEC API methods
    """
    def __init__(self, method_helper: _MethodsHelper):
        self._mh = method_helper
        self.url = "dns/"
    
    def get_record(self, domain:str):
        url = self.url+ f"getDbssecRecords/{domain}"
        resp = self._mh._requester(url)
        return resp["records"]
    
    def add_record(self, domain:str, key_tag, alg, digest_type, digest, max_sig_life, key_data_flags, key_data_protocol, key_data_algo, key_data_pub_key): #TODO figure out datatypes
        url = self.url+ f"createDnssecRecord/{domain}"
        params = {
            "keyTag": key_tag,
            "alg": alg,
            "digestType": digest_type,
            "digest": digest,
            "maxSigLife": max_sig_life,
            "keyDataFlags": key_data_flags,
            "keyDataProtocol": key_data_protocol,
            "keyDataAlgo": key_data_algo,
            "keyDataPubKey": key_data_pub_key
            }
        resp = self._mh._requester(url, params)
        return resp # Returns nothing
        
    def delete_record(self, domain:str, key_tag:str|int):
        url = self.url+ f"deleteDnssecRecord/{domain}/{key_tag}"
        resp = self._mh._requester(url)
        return resp # Returns nothing
    

class _SSLMethods:
    def __init__(self, method_helper: _MethodsHelper):
        self._mh = method_helper
        self.url = "ssl/"
    
    def get_ssl_bundle(self, domain:str):
        url = self.url+ f"getDbssecRecords/{domain}"
        resp = self._mh._requester(url)
        return resp
    