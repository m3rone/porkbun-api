from os import getenv
from urllib import request, error, parse
import json

class PorkbunError(Exception):
    ...

def _defaultKeysIfNone(): #api, secret):
    #keylist = (api, secret)
    if all(envkeys := (getenv("PORKBUN_APIKEY", ""), getenv("PORKBUN_SECRETAPIKEY", ""))): # defaults set to "" because pyright cant comprehend that all() checking whether both env vars exist
        return envkeys
    # elif not any(keylist): # Deprecate global var option
    #   return (APIKEY, SECRETAPIKEY) 
    # elif all(keylist):
    #   return keylist
    return ("", "")

#def _checkErr(response):
#    if response.status == 400:
#        errMsg = json.load(response.read().decode("utf-8"))["message"]
#        raise PorkbunError(errMsg)

def _get(url:str):
    keys = _defaultKeysIfNone()
    headers = {
            "X-API-Key": f"{keys[0]}",
            "X-Secret-API-Key": f"{keys[1]}"
            }
    req = request.Request(url=url, headers=headers, method="GET")
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _post(url:str, body:dict = {}):
    keys = _defaultKeysIfNone()
    headers = {
            "Content-Type": "application/json",
            "X-API-Key": f"{keys[0]}",
            "X-Secret-API-Key": f"{keys[1]}"
            }
    payload = json.dumps(body).encode("utf-8")
    req = request.Request(url=url, data=payload, headers=headers, method="POST")
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))
