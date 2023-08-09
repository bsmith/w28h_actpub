#!python3

import requests
import logging
import json

enable_http_debug = False

if enable_http_debug:
    # Enabling debugging at http.client level (requests->urllib3->http.client)
    # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # the only thing missing will be the response.body which is not logged.
    from http.client import HTTPConnection
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

if person_url is None:
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

outbox = r.json()
if outbox['type'] != 'OrderedCollection':
    raise Exception("Expected the outbox to be an OrderedCollection")

outbox_totalItems = outbox['totalItems']
outbox_first_url = outbox['first']
outbox_last_url = outbox['last']

outbox_contents = []

cur_url = outbox_first_url

while cur_url is not None:
    print("Fetching page at %s" % cur_url)
    r = requests.get(cur_url, headers={ "Accept": "application/json" })
    r.raise_for_status()
    page = r.json()

    outbox_contents.extend(page["orderedItems"])
    print("Got %d items of %d" % (len(outbox_contents), outbox_totalItems))

    del page['orderedItems']
    print(json.dumps(page, indent=4))

    if "next" in page:
        cur_url = page["next"]
    else:
        cur_url = None

print("writing to outbox.json")
with open("outbox.json", "w") as file:
    json.dump(outbox_contents, file, indent=4)

print("finished")