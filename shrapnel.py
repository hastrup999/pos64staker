#!/usr/bin/env python3
import sys
import json
import stakerlib
import random
import time

CHAIN = 'CFEKPAY'
try:
    rpc_connection = stakerlib.def_credentials(CHAIN)
except Exception as e:
    sys.exit(e)
balance = float(rpc_connection.getbalance())
address = 'PUT YOUR ADDRESS HERE'
print(address)
#time.sleep(33)
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

while True:
    print('Address Count: ' + str(address_count))
    average = float(balance) / int(address_count)
    print('Average utxo size: ' + str(average))
    variance = int(input('Enter percentage of variance: '))
    minsize = round(float(average) * (1-(variance/100)),2)
    maxsize = round(average + float(average) * (variance/100),2)
    print('Min size: ' + str(minsize))
    print('Max size: ' + str(maxsize))
    ret = input('Are you happy with these? ').lower()
    if ret.startswith('y'):
        break

# function to do sendmany64 UTXOS times, locking all UTXOs except change
def sendmanyloop(rpc_connection):
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
                if totalamnt > balance-(balance*0.01):
                    sendmany64_txid = rpc_connection.sendmany("", addresses_dict, 0)
                    print(print("Sending Funds to "+str(j)+" addresses. TXID: "+sendmany64_txid))
                    totalamnt = 0
                    finished = True
                    break
                

sendmanyloop(rpc_connection)


