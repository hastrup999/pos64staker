#!/usr/bin/env python3

import stakerlib
from slickrpc import Proxy
from datetime import datetime
import json
import os

NAME = input('Please input your name: ')

try:
    os.makedirs("/tmp/DUMMY")
except FileExistsError:
    # directory already exists
    pass
    
stakerlib.start_daemon('DUMMY', True)
rpc = Proxy("http://%s:%s@127.0.0.1:%d" % ('DUMMYUSER', 'DUMMYPASS', 9181))

print(rpc.getinfo())

stakerlib.genaddresses('PRIVATE', rpc)


with open('PRIVATE.json') as key_list:
    json_data = json.load(key_list)
    addrs = []
    for i in json_data:
        addrs.append(i[3])


with open('participants.json') as part:
    participants = json.load(part)
participants[NAME] = addrs
print(participants)
f = open("participants.json", "w+")
f.write(json.dumps(participants))

rpc.stop()

print('done')