#!/usr/bin/env python3
import sys
import json
import os.path
import stakerlib

if os.path.isfile("list.json"):
    print('Already have list.json, move it if you would like to '
          'generate another set.You can use importlist.py script to import'
          ' the already existing list.py to a given chain.')
    sys.exit(0)

CHAIN = input('Please specify chain: ')
AMOUNT = input('Enter amount of address to make:')
# create rpc_connection
try:
    rpc_connection = stakerlib.def_credentials(CHAIN)
except Exception as e:
    sys.exit(e)
    
segids = []
while len(segids) < int(AMOUNT):
    genvaldump_result = stakerlib.genvaldump(rpc_connection)
    segids.append(genvaldump_result)

# save output to list.py
print('Success! list.json created. '
      'THIS FILE CONTAINS PRIVATE KEYS. KEEP IT SAFE.')
f = open("list.json", "w+")
f.write(json.dumps(segids))
