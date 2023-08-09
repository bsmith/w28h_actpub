#!python3

import requests
import json

# start with a webfinger request
r = requests.get("https://mikrotik.social/.well-known/webfinger", { "resource": "acct:mikrotik@mikrotik.social" })
r.raise_for_status()
webfinger = r.json()
print(webfinger)

print("got webfinger for %s" % webfinger["subject"])
actpub_url = None
for link in webfinger['links']:
    if link['rel'] == "self" and link['type'] == "application/activity+json":
        actpub_url = link['href']
        break

if actpub_url == None:
    raise Exception("Couldn't find an ActivityPub self link")
print("Got ActivityPub self link: %s" % actpub_url)
