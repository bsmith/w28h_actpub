#!python3

import requests
import logging
import json

enable_http_debug = False

if enable_http_debug:
    # Enabling debugging at http.client level (requests->urllib3->http.client)
    # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # the only thing missing will be the response.body which is not logged.
    try: # for Python 3
        from http.client import HTTPConnection
    except ImportError:
        from httplib import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


# start with a webfinger request
r = requests.get("https://mikrotik.social/.well-known/webfinger", { "resource": "acct:mikrotik@mikrotik.social" }, headers={ "Accept": "application/json" })
r.raise_for_status()
webfinger = r.json()

print("got webfinger for %s" % webfinger["subject"])
person_url = None
for link in webfinger['links']:
    if link['rel'] == "self" and link['type'] == "application/activity+json":
        person_url = link['href']
        break

if person_url == None:
    raise Exception("Couldn't find an ActivityPub self link")
print("Got ActivityPub self link: %s" % person_url)

# Next get the Person object using this ActivityPub self link
r = requests.get(person_url, headers={ "Accept": "application/json" })
r.raise_for_status()
person = r.json()

print(json.dumps(person, indent=4))

# Let's look in the outbox
outbox_url = person['outbox']
print("outbox is %s" % outbox_url)
r = requests.get(outbox_url, headers={ "Accept": "application/json" })
r.raise_for_status()
print(r.text)