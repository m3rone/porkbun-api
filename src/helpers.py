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

def _get(url:str):
    keys = _defaultKeysIfNone()
    headers = {
            "X-API-Key": f"{keys[0]}",
            "X-Secret-API-Key": f"{keys[1]}"
            }

def _post(url:str, body:dict):
    keys = _defaultKeysIfNone()
    headers = {
            "Content-Type": "application/json",
            "X-API-Key": f"{keys[0]}",
            "X-Secret-API-Key": f"{keys[1]}"
            }
