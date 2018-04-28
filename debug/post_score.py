#!/usr/bin/env python3
import sys
import requests
import yml
import os
import hashlib

if len(sys.argv != 5):
    return "{} GAME SCORE_NAME NAME SCORE"
    sys.exit(0)

_, game, score_type, name, score = sys.argv

DOCKER_COMPOSE_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'docker-compose.yml',
)

with open(DOCKER_COMPOSE_PATH, 'r') as stream:
    settings = yml.load(stream)

secret = 'RatatosK'
port = "5000"
service = None

for service in settings['services'].values():
    try:
        secret = [
            e.split('=')[1] for e in service['environment']
            if e.startswith('HIGHSCORE_SECRET')
        ][0]
        port = service['ports'][0].split(":")[0]
        service = service
    except (KeyError, IndexError):
        pass
    else:
        break

if service is None:
    secret = 'RatatosK'
    port = "5000"
    service = ""
else:
    if 'environment' in service:
        service = [
            e.split('=')[1] for e in service['environment']
            if e.startswith('HIGHSCORE_APP_ROOT')
        ]
        service = service[0] if service else ''
    else:
        service = ''

checksum = hashlib.md5(
    "{}{}{}".format(name, score, secret).encode('utf8'),
).hexdigest()

print(
    "localhost:{}{}/highscore/{}/{}".format(
        port, root, game, score_type,
    ),
)
print("name {} score {} checksum {}".format(name, score, checksum))
sys.exit(0)

requests.post(
    "localhost:{}{}/highscore/{}/{}".format(
        port, root, game, score_type,
    ),
    data = {
        "name": name,
        "score": score,
        "checkSum": checksum,
    }
)
