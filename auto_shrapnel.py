#!/usr/bin/env python3
import sys
import json
import stakerlib
import random
import time
import math

CHAIN = 'CFEKPAY'
variance = 5
address = 'ENTER YOUR ADDRESS'

try:
    rpc_connection = stakerlib.def_credentials(CHAIN)
except Exception as e:
    sys.exit(e)

paymentinfo = rpc_connection.paymentsinfo("[%225bbc56201b1a61bdba4f708dc64928ad7a854f2e5137c93eba309f95756d02d4%22]")
snapshot = rpc_connection.getsnapshot(str(3999))
blockcount = rpc_connection.getblockcount()
median_address = int(snapshot['total_addresses']/2)
balance = float(rpc_connection.getbalance())
middle_balance = snapshot['addresses'][median_address]['amount']    
spread	= math.floor(float(balance) / float(middle_balance))
print("")

print('Balance: '+ str(balance))
print('Addresses on chain : ' + str(snapshot['total_addresses']))
print('Using ' + str(spread) + ' addresses to cluster around '+str(middle_balance)+'.')

print("")
print("Snapshot Height: "+str(paymentinfo['min_release_height']))
print("Block height: "+str(blockcount))
block_gap = paymentinfo['min_release_height'] - blockcount
#block_gap = 5
while block_gap > 15:
    paymentinfo = rpc_connection.paymentsinfo("[%225bbc56201b1a61bdba4f708dc64928ad7a854f2e5137c93eba309f95756d02d4%22]")
    snapshot = rpc_connection.getsnapshot(str(3999))
    blockcount = rpc_connection.getblockcount()
    median_address = int(snapshot['total_addresses']/2)
    balance = float(rpc_connection.getbalance())
    middle_balance = snapshot['addresses'][median_address]['amount']    
    spread  = math.floor(float(balance) / float(middle_balance))
    print("")

    print('Balance: '+ str(balance))
    print('Addresses on chain : ' + str(snapshot['total_addresses']))
    print('Using ' + str(spread) + ' addresses to cluster around '+str(middle_balance)+'.')

    print("")
    print("Snapshot Height: "+str(paymentinfo['min_release_height']))
    print("Block height: "+str(blockcount))
    block_gap = paymentinfo['min_release_height'] - blockcount
    print(str(block_gap)+" blocks remaining...")
    time.sleep(2*block_gap)

txid = rpc_connection.sendtoaddress(address, str(balance-0.1))
print("Sending all funds ("+str(balance)+" "+CHAIN+") to "+address+".")
print("TXID: "+txid)

with open('list.json') as key_list:
    json_data = json.load(key_list)
    address_count = len(json_data)
    time.sleep(10)
while txid in rpc_connection.getrawmempool():
    print('Waiting for transaction to confirm...')
    time.sleep(10)

average = float(balance) / int(spread)
print('Average utxo size: ' + str(average))
minsize = round(float(average) * (1-(variance/100)),2)
maxsize = round(average + float(average) * (variance/100),2)
print('Min size: ' + str(minsize))
print('Max size: ' + str(maxsize))
print("")

# function to do sendmany64 UTXOS times, locking all UTXOs except change
def sendmanyloop(rpc_connection, spread):
    with open('list.json') as key_list:
        json_data = json.load(key_list)
        finished = False
        totalamnt = 0 
        j = 0
        while finished == False:
            totalamnt = 0
            addresses_dict = {}
            for i in range(len(json_data)):
                address = json_data[i][3]
                addresses_dict[address] = round(random.uniform(minsize,maxsize),0)
                totalamnt = totalamnt + addresses_dict[address]
                j += 1
                if j == 40:
                    sendmany64_txid = rpc_connection.sendmany("", addresses_dict, 0)
                    print("Sending Funds to 40 addresses. TXID:  "+sendmany64_txid)
                    addresses_dict = {}
                    time.sleep(5)
                    j = 0
                if totalamnt > balance-(balance*0.001):
                    sendmany64_txid = rpc_connection.sendmany("", addresses_dict, 0)
                    print(print("Sending Funds to "+str(j)+" addresses. TXID: "+sendmany64_txid))
                    totalamnt = 0
                    finished = True
                    break
                if i > spread:
                    finished = True
                    break
                



sendmanyloop(rpc_connection, spread)
