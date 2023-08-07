import base64
import io
import json
import os
import random
import requests
import sys
import time

iters = 10
max_wait = 15
lines = 8000

owner = "alexdotc"
repo = "gh-api-test"
path = "the.file"

url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

token = os.environ.get("GH_TOKEN")
if not token:
    print("No token in env!", file=sys.stderr)
    sys.exit(1)

def get():
    r = requests.get(url, 
      headers={"Accept": "application/vnd.github+json",
               "Authorization": "Bearer " + token,
               "X-Github-Api-Version": "2022-11-28"})
    r.raise_for_status()
    j = r.json()
    return j['sha'],j['content']

def update(sha, content):
    seconds = random.randint(5,max_wait)
    line = random.randint(0,lines-1)

    message = f"Update SHA {sha}, line {line}, after {seconds} seconds"
    newcontent = content.copy()
    newcontent[line] = sha

    newcontent = base64.b64encode("\n".join(newcontent).encode()).decode()
    time.sleep(seconds)
    
    r = requests.put(url,
      headers={"Accept": "application/vnd.github+json",
               "Authorization": "Bearer " + token,
               "X-Github-Api-Version": "2022-11-28"},
      data=json.dumps({"message": message, "sha": sha, "content": newcontent}))

    r.raise_for_status()
    j = r.json()

    return line, j['content']['sha']

# start
print("GET")
sha, content = get()
content = base64.b64decode(content).decode().splitlines()
print("UPDATE")
line, update_sha = update(sha, content)
print(f"Updated to sha {update_sha}")

# loop
for n in range(0, iters):
    print("GET")
    new_sha, content = get()
    print("VERIFY GET")
    content = base64.b64decode(content).decode().splitlines()
    try:
        assert new_sha == update_sha
    except AssertionError:
        print(f"Got old SHA {new_sha} -- Expected {update_sha} !", file=sys.stderr)
        raise
    try:
        assert content[line] == sha # this sometimes fails and sometimes doesnt. it usually fails very quickly, within a few iterations
    except AssertionError:
        print(f"Content at line {line} is {content[line]} -- Expected {sha} !", file=sys.stderr)
        raise
    sha = new_sha
    print("UPDATE")
    line, update_sha = update(sha, content)
    print(f"Updated to sha {update_sha}")
