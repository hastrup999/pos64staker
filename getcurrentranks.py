#!/usr/bin/env python3
import sys
import json
import stakerlib
import random

CHAIN = 'CFEKPAY'
try:
    rpc_connection = stakerlib.def_credentials(CHAIN)
except Exception as e:
    sys.exit(e)
with open('list.json') as key_list:
    json_data = json.load(key_list)
    TUTXOS = len(json_data)

snapshot = rpc_connection.getsnapshot(str(3999))
dailysnapshot = rpc_connection.getsnapshot(str(-1))
paymentsinfo = rpc_connection.paymentsinfo('["5bbc56201b1a61bdba4f708dc64928ad7a854f2e5137c93eba309f95756d02d4"]')
#print(paymentsinfo)
bottom = paymentsinfo['bottom']
top = paymentsinfo['top']
n = 0
bottom_balance = 0
top_balance = 0

for i in range(len(dailysnapshot['addresses'])):
    if i == bottom:
        bottom_balance = dailysnapshot['addresses'][i]['amount']
    if i == top:
        top_balance = dailysnapshot['addresses'][i]['amount']
    for address in json_data:
        if address[3] == dailysnapshot['addresses'][i]['addr']:
            #print('found rank ' + str(i) + ' : ' + address[3])
            if i > bottom and i < top:
                n = n + 1
                #print(str(i) + ' within range: ' + str(bottom) + ' - ' + str(top))
print('You have: ' + str(n) + ' addresses within the range ' + str(bottom) + ' - ' + str(top) + ' in the current daily snapshot')
print('Balance of bottom address: ' + str(bottom_balance))
print('Balance of top address: ' + str(top_balance))
print('')

top = 0
bottom = 3999
for i in range(len(snapshot['addresses'])):
    for address in json_data:
        if address[3] == snapshot['addresses'][i]['addr']:
            if i > top:
                top = i
                top_balance = snapshot['addresses'][i]['amount']
            if i < bottom:
                bottom = i 
                bottom_balance = snapshot['addresses'][i]['amount']
print('Your address currently fall into the following range: ' + str(bottom) + '-' + str(top))
print('Bottom balance: ' + str(bottom_balance))
print('Top Balance: ' + str(top_balance))
print('')

print('There are : ' + str(snapshot['total_addresses']) + ' addresses on chain at block: ' + str(snapshot['ending_height']))
median_address = int(snapshot['total_addresses']/2)
print('This is the middle address right now: ' + str(snapshot['addresses'][median_address]))

balance = float(rpc_connection.getbalance())
average = float(balance) / float(snapshot['addresses'][median_address]['amount'])

print('You should use ' + str(average) + ' addresses to cluster them in the middle, with your current balance of: '+ str(balance))
