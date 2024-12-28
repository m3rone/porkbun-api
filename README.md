<div align="center">
  <img src="https://github.com/user-attachments/assets/ddda2ca6-b393-4629-9111-209362dda847" alt="porkbun-api project logo" width="224">
  <h1>Porkbun API</h1>
</div>

This is an API wrapper for Porkbun written in Python with few extra features/shortcuts.

[Porkbun API documentation](https://porkbun.com/api/json/v3/documentation)

This project is subject to breaking changes as Porkbun API may change and/or become invalid. I do not guarantee anything.

### Installing
You can install this through PyPi with pip:
`pip install porkbun-api`

Or you can grab a .whl or .tar.gz file from [Github releases](https://github.com/m3rone/porkbun-api/releases).

### Usage

This wrapper supports everything other than operations with ID's for now.

Available functions and arguments:
**Please keep in mind every function requires an `apikey` and `secretapikey` arguments**, but you can set **`APIKEY`** and **`SECRETAPIKEY`** variables in the code or **`PORKBUN_APIKEY`** and **`PORKBUN_SECRETAPIKEY`** environment variables with their respective values and not have to give keys as arguments at every function call.

Key precedence is environment variable > code variable > function argument. Please note at the moment you can not mix and match different ways of providing your keys

- ping()
  - Optional: `ipv4only` *(takes True or False and returns IPv4 only if True and IPv6 if available otherwise. Default = True)*.
  - Returns IP address.
- nsupdate() 
  - Requires `domain` *(takes a string of the domain you want to work on)* and `nslist` *(a list containing nameservers)*.
  - Does not return anything, changes the authoritative nameservers for given domain.
- create()
  - Requires `domain`, `rtype` *(string of the record type such as A, AAAA, MX, etc)*, and `content` *(string value for said request type such as the IP address)*.
  - Optional: `subdomain` *(string subdomain for said domain)* and `ttl` *(integer number for time to live, default and minimum for Porkbun is 600)*. `prio` *(integer priority for record types that support it)*
  - Does not return anything. Creates a new DNS record with given arguments.
- read()
  - Requires `domain`, `rtype`.
  - Optional: `subdomain`.
  - Returns a [list of records](https://porkbun.com/api/json/v3/documentation#DNS%20Retrieve%20Records%20by%20Domain,%20Subdomain%20and%20Type).
- update()
  - Requires `domain`, `rtype`, and `content`.
  - Optional: `name` `ttl`, and `prio`.
  - Does not return anything. Updates the matching record with given `content`
- delete()
  - Requires `domain` and `rtype`.
  - Optional `subdomain`.
  - Does not return anything. Deletes the matching record.
- ddns_update()
  - Requires `domain`.
  - Optional: `ip` *(the string IP address to update the record with. If not given, uses the return of ping() as IP)*, `subdomain`, and `ipv4only`.
  - Does not return anything. Updates the `domain` or `subdomain`'s A or AAAA record depending on the IP type given.

### Examples

```py
import porkbun_api as pb
from time import sleep # only as an example, not required.

pb.APIKEY = "pk1_..." # or the env var PORKBUN_APIKEY="pk1_..."
pb.SECRETAPIKEY = "sk1_..." # or the env var PORKBUN_SECRETAPIKEY="sk1_..."

print(pb.ping())

pb.create(domain = "m3r.one", rtype = "A", content = "23.94.123.251")

pb.delete(domain = "m3r.one", rtype = "A", subdomain = "bin", apikey = "pk1_overwrite-the-variable", secretapikey = "sk1_overwrite-the-variable")

while True:
  pb.ddns_update(domain = "m3r.one")
  sleep(86400)
```

### Notes
It is recommended to use `try` - `except` blocks with every function because it raises a `PorkbunError` exception if Porkbun returns an error for whatever reason. Plus, `requests` library will raise exceptions itself if something goes wrong with the request.

Feel free to open issues or contact me in case you wish to see extra features added.

---
This project is not affiliated with Porkbun LLC.
