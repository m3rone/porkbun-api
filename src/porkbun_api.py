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

ALLOWEDTYPES = ["A", "MX", "CNAME", "ALIAS", "TXT", "NS", "AAAA", "SRV", "TLSA", "CAA"]

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
            
    
    
class Porkbun(_MethodsHelper):
    def __init__(self, apikey:str, secretapikey:str): #TODO docstring
        super().__init__(apikey, secretapikey)
        
        # Inititiate the "subclasses".  They're not really subclasses but IDK what else to call them
        self.domain = _DomainMethods(apikey, secretapikey)
        self.dns = _DNSMethods(apikey, secretapikey)
        self.dnssec = _DNSSECMethods(apikey, secretapikey)
        self.ssl = _SSLMethods(apikey, secretapikey)
    
    def ping(self): # Requires auth
        url = "ping"
        resp = self._requester(url)
        return resp_dict.Ping.from_json(resp)
    

class _DomainMethods(_MethodsHelper):
    def __init__(self, apikey:str, secretapikey:str): #TODO docstring
        super().__init__(apikey, secretapikey)
        self.url = "domain/"
    
    def get_pricing(self): #TODO DOES NOT WORK #TODO allow to run without auth
        url = "/pricing/get"
        resp = self._requester(url)
        return resp['pricing']
    
    def list_all(self, start:Optional[int]=None, include_labels:bool=False):
        url = self.url+ "listAll"
        params = {
            "start": start,
            "includeLabels": include_labels
        }
        resp = self._requester(url, params=params)
        return resp['domains']
    
    def check_availability(self, domain:str): # TODO could also be called "check" to match documentation
        url = self.url+ f"checkDomain/{domain}"
        resp = self._requester(url)
        return resp
    
    def get_nameservers(self, domain:str):
        url = self.url+ f"getNs/{domain}"
        resp = self._requester(url)
        return resp
    
    def update_nameservers(self, domain:str, nameservers:list):
        url = self.url+ f"updateNs/{domain}"
        params = {"ns": nameservers}
        resp = self._requester(url, params)
        return resp
    
    def get_url_forwarding(self):
        url = self.url+ f""
        resp = self._requester(url)
        return resp
    
    def add_url_forwarding(self, domain:str, location:str, forward_type:FORWARDTYPES, include_path:bool, also_forward_subdomains:bool, subdomain:Optional[str]=None):
        url = self.url+ f"addUrlForward/{domain}"
        params = {
            "subdomain": subdomain,
            "location": location,
            "type": forward_type,
            "includePath": "yes" if include_path else "no",
            "wildcard": "yes" if also_forward_subdomains else "no",
        }
        resp = self._requester(url, params=params)
        return resp
    
    def delete_url_forwarding(self):
        url = self.url+ f""
        resp = self._requester(url)
        return resp
    
    def get_glue_record(self): #TODO is it a single record or multiple?
        url = self.url+ f""
        resp = self._requester(url)
        return resp
    
    def add_glue_record(self):
        url = self.url+ f""
        resp = self._requester(url)
        return resp
    
    def update_glue_record(self):
        url = self.url+ f""
        resp = self._requester(url)
        return resp
    
    def delete_glue_record(self):
        url = self.url+ f""
        resp = self._requester(url)
        return resp
    

class _DNSMethods(_MethodsHelper):
    def __init__(self, apikey:str, secretapikey:str): #TODO docstring
        super().__init__(apikey, secretapikey)
        
    
    def get_record(self, domain:str, subdomain:Optional[str]=None, record_type:Optional[str]=None, record_id:Optional[int|str]=None):
        if record_id == None and (subdomain == None or record_type == None):
            raise ValueError("Must provide a DNS record ID or subdomain and record type")
        
        url = f"/dns/retrieveByNameType/{domain}/"
        if record_id != None:
            url += record_id
        else:
            url += f"{record_type}/{subdomain}"

        resp = requests.post(url=URL_BASE+url,json=auth_json)
        if resp.status_code != 200:
            raise Exception(resp) # TODO flesh this out and log the error somewhere
        elif len(jloads(resp.text)['records']) == 0:
            raise Exception(resp) #TODO bad
        else:
            return jloads(resp.text)['records'][0] # Select the record
    
    def add_record(self): #TODO could also be "create_record" to match documentation
        pass
    
    def update_record(self, domain:str, content:str, record_id:Optional[int|str], name:Optional[str]=None, record_type:Optional[str]=None, ttl:Optional[int]=None, priority:Optional[int]=None, notes:Optional[int]=None): # Record is optional in case I decide to add edting by subdomain and type later
        # if name is not provided it'll wipe it out 
        if name == None or ttl == None or priority == None or notes == None or record_type == None: # Get the current record information to fill in
            record = porkbun_get_record(domain=domain, record_id=record_id)
        
        query = f"dns/edit/{domain}/{record_id}"
        
        changes = {
            **auth_json, # Add the auth stuff to the json we're gonna send
            "name": name if name != None else record['name'],
            "type": record_type if record_type != None else record['type'],
            "content": content,
            "ttl": ttl if ttl != None else record['ttl'],
            "prio": priority if priority != None else record['prio'],
            "notes": notes if notes != None else record['notes']
            }
        
        resp = requests.post(url=URL_BASE+query,json=changes)
        if resp.status_code != 200 or jloads(resp.text)['status'] != "SUCCESS":
            raise Exception(resp) # TODO flesh this out and log the error somewhere
        
    def delete_record(self):
        pass
    
class _DNSSECMethods(_MethodsHelper):
    def __init__(self, apikey:str, secretapikey:str): #TODO docstring
        super().__init__(apikey, secretapikey)
    
    def get_record(self, domain:str, subdomain:Optional[str]=None, record_type:Optional[str]=None, record_id:Optional[int|str]=None):
        if record_id == None and (subdomain == None or record_type == None):
            raise ValueError("Must provide a DNS record ID or subdomain and record type")
        
        url = f"/dns/retrieveByNameType/{domain}/"
        if record_id != None:
            url += record_id
        else:
            url += f"{record_type}/{subdomain}"

        resp = requests.post(url=URL_BASE+url,json=auth_json)
        if resp.status_code != 200:
            raise Exception(resp) # TODO flesh this out and log the error somewhere
        elif len(jloads(resp.text)['records']) == 0:
            raise Exception(resp) #TODO bad
        else:
            return jloads(resp.text)['records'][0] # Select the record
    
    def add_record(self): #TODO could also be "create_record" to match documentation
        pass
    
    def update_record(self, domain:str, content:str, record_id:Optional[int|str], name:Optional[str]=None, record_type:Optional[str]=None, ttl:Optional[int]=None, priority:Optional[int]=None, notes:Optional[int]=None): # Record is optional in case I decide to add edting by subdomain and type later
        # if name is not provided it'll wipe it out 
        if name == None or ttl == None or priority == None or notes == None or record_type == None: # Get the current record information to fill in
            record = porkbun_get_record(domain=domain, record_id=record_id)
        
        query = f"dns/edit/{domain}/{record_id}"
        
        changes = {
            **auth_json, # Add the auth stuff to the json we're gonna send
            "name": name if name != None else record['name'],
            "type": record_type if record_type != None else record['type'],
            "content": content,
            "ttl": ttl if ttl != None else record['ttl'],
            "prio": priority if priority != None else record['prio'],
            "notes": notes if notes != None else record['notes']
            }
        
        resp = requests.post(url=URL_BASE+query,json=changes)
        if resp.status_code != 200 or jloads(resp.text)['status'] != "SUCCESS":
            raise Exception(resp) # TODO flesh this out and log the error somewhere
        
    def delete_record(self):
        pass

class _SSLMethods(_MethodsHelper):
    def __init__(self, apikey:str, secretapikey:str): #TODO docstring
        super().__init__(apikey, secretapikey)
    
    