#!/usr/bin/env python3
import sys
import json
import os.path
import stakerlib

if os.path.isfile("list.json"):
    with open('list.json') as key_list:
        json_data = json.load(key_list)
        TUTXOS = len(json_data)

CHAIN = input('Please specify chain: ')
AMOUNT = int(input('Enter amount of address to make: '))

if AMOUNT < len(json_data):
    print('Already have more address than this, please backup list.json and create new addresses.)
    sys.exit()

# create rpc_connection
try:
    rpc_connection = stakerlib.def_credentials(CHAIN)
except Exception as e:
    sys.exit(e)

while len(json_data) < AMOUNT:
    genvaldump_result = stakerlib.genvaldump(rpc_connection)
    json_data.append(genvaldump_result)

# save output to list.json
print('Success! list.json created. '
      'THIS FILE CONTAINS PRIVATE KEYS. KEEP IT SAFE.')
f = open("list.json", "w+")
f.write(json.dumps(json_data))
