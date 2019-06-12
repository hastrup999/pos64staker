#!/usr/bin/env python3
import sys
import stakerlib 
import json
   
# function to unlock ALL lockunspent UTXOs
def unlockunspent():
    try:
        listlockunspent_result = rpc_connection.listlockunspent()
    except Exception as e:
        sys.exit(e)
    unlock_list = []
    for i in listlockunspent_result:
        unlock_list.append(i)
    try:
        lockunspent_result = rpc_connection.lockunspent(True, unlock_list)
    except Exception as e:
        sys.exit(e)
    return(lockunspent_result)
    
def extract_segid(_segid,unspents):
    ret = []
    for unspent in unspents:
        if unspent['segid'] == _segid:
            unspent['amount'] = float(unspent['amount'])
            ret.append(unspent)
    return(ret)

CHAIN = input('Please specify chain: ')
try:
    rpc_connection = stakerlib.def_credentials(CHAIN)
except Exception as e:
    sys.exit(e)
balance = float(rpc_connection.getbalance())
print('Balance: ' + str(balance))

PERC = int(input("Please specify the percentage of balance to lock: "))
if PERC < 1:
    sys.exit('Cant lock 0%. Exiting.')

# get listunspent
try:        
    listunspent_result = rpc_connection.listunspent()
except Exception as e:
    sys.exit(e)

try:
    with open('list.json') as list:
        segid_addresses = json.load(list)
except:
    print('Could not load list.json please make sure it is in the directory where this script is located. Exiting')
    sys.exit(0)

# sort into utxos per segid.
segids = []

for i in range(0,63):
    segid = extract_segid(i, listunspent_result)
    segids.append(segid)

lockunspent_list = []
# Sort it by value and confirms. We want to keep large and old utxos. So largest and oldest at top.
# When the wallet has small number of utxo per segid ( < 10 )the percentage should be static 50, other % give unexpected results.
for segid in segids:
    # likley some improvment here age vs. size ? 
    # there should maybe be a utxo score, that includes age and size and locks utxos with highest score.
    segid = sorted(segid, key=lambda x : (-x['amount'], -x['confirmations']))
    numutxo = int(len(segid) * (PERC/100))
    i = 0
    for unspent in segid:
        output_dict = {
            "txid": unspent['txid'],
            "vout": unspent['vout']
            }
        lockunspent_list.append(output_dict)
        i = i + 1
        if i >= numutxo:
            break

# Lock % defined of each segids utxos.
lockunspent_result = rpc_connection.lockunspent(False, lockunspent_list)

# get listunspent
try:        
    listunspent_result = rpc_connection.listunspent()
except Exception as e:
    sys.exit(e)
totalbalance = 0
for unspent in listunspent_result:
    totalbalance = float(totalbalance) + float(unspent['amount'])
    
print('Balance avalibe to send: ' + str(totalbalance))
    
amount = float(input('Amount? '))
if amount < 0 or amount > totalbalance:
    unlockunspent()
    sys.exit('Too poor!')
    
# find out what segids have staked the least in the last day
try:
    getlastsegidstakes_result = rpc_connection.getlastsegidstakes(1440)
except Exception as e:
    sys.exit(e)
usable_segids = []
averagestakes = int((1440 - int(getlastsegidstakes_result['PoW'])) / 64)
for _segid, stakes in getlastsegidstakes_result['SegIds'].items():
    if stakes < averagestakes:
        usable_segids.append(_segid)

addresses_dict = {}
for segid in usable_segids:
    address = segid_addresses[int(segid)][3]
    # there should be a weight calculated and applied for segids with less stakes in the last 24H to get more coins? 
    addresses_dict[address] = amount / len(usable_segids)

print('Sending ' + str(addresses_dict))
ret = input('Are you happy with these? ').lower()
if ret.startswith('n'):
    unlockunspent()
    sys.exit('You are not happy?')

# send coins.
sendmany_result = rpc_connection.sendmany("", addresses_dict, 0)

# unlock all locked utxos
unlockunspent()
print('Success: ' + sendmany_result)
