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
balance = float(rpc_connection.getbalance())
with open('list.json') as key_list:
    json_data = json.load(key_list)
    TUTXOS = len(json_data)
print('Balance: ' + str(balance))

while True:
    print('Total number of UTXOs: ' + str(TUTXOS))
    average = float(balance) / int(TUTXOS)
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
        while finished == False:
            totalamnt = 0
            addresses_dict = {}
            for i in range(len(json_data)):
                address = json_data[i][3]
                addresses_dict[address] = round(random.uniform(minsize,maxsize),0)
                totalamnt = totalamnt + addresses_dict[address]
                if totalamnt > balance-(balance*0.01):
                    totalamnt = 0
                    break
            if totalamnt > balance-(balance*0.02):
                finished = True
            # make rpc call, issue transaction
        print(str(totalamnt))
        sendmany64_txid = rpc_connection.sendmany("", addresses_dict, 0)
    return(sendmany64_txid)

sendmanyloop_result = sendmanyloop(rpc_connection)
print(sendmanyloop_result)
