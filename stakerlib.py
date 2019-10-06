import platform
import os
import re
import json
import random
import base58
import binascii
import hashlib
import time
import codecs
from slickrpc import Proxy


# fucntion to define rpc_connection
def def_credentials(chain):
    rpcport = '';
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    if os.path.isfile(coin_config_file):
        with open(coin_config_file, 'r') as f:
            for line in f:
                l = line.rstrip()
                if re.search('rpcuser', l):
                    rpcuser = l.replace('rpcuser=', '')
                elif re.search('rpcpassword', l):
                    rpcpassword = l.replace('rpcpassword=', '')
                elif re.search('rpcport', l):
                    rpcport = l.replace('rpcport=', '')
        if len(rpcport) == 0:
            if chain == 'KMD':
                rpcport = 7771
            else:
                print("rpcport not in conf file, exiting")
                print("check " + coin_config_file)
                exit(1)

        return (Proxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport))))
    else:
        errmsg = coin_config_file+" does not exist! Please confirm "+str(chain)+" daemon is installed"
        print(colorize(errmsg, 'red'))
        exit(1)


def user_input(display, input_type):
    u_input = input(display)
    if u_input == 'q':
        print('Exiting to previous menu...\n')
        return('exit')
    if isinstance(int(u_input), input_type) and input_type is int:
        return int(u_input)
    if not isinstance(u_input, input_type):
        print('input must be a ' + str(input_type) + '\n')
        return('exit')
    else:
        return(u_input)
    

# generate address, validate address, dump private key
def genvaldump(rpc_connection):
    # get new address
    address = rpc_connection.getnewaddress()
    # validate address
    validateaddress_result = rpc_connection.validateaddress(address)
    segid = validateaddress_result['segid']
    pubkey = validateaddress_result['pubkey']
    address = validateaddress_result['address']
    # dump private key for the address
    privkey = rpc_connection.dumpprivkey(address)
    # function output
    output = [segid, pubkey, privkey, address]
    return(output)


def colorize(string, color):
    colors = {
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'green': '\033[92m',
        'red': '\033[91m'
    }
    if color not in colors:
        return string
    else:
        return colors[color] + string + '\033[0m'


# function to convert any address to different prefix 
# also useful for validating an address, use '3c' for prefix for validation
def addr_convert(prefix, address):
    rmd160_dict = {}
    ripemd = base58.b58decode_check(address).hex()[2:]
    net_byte = prefix + ripemd
    bina = binascii.unhexlify(net_byte)
    sha256a = hashlib.sha256(bina).hexdigest()
    binb = binascii.unhexlify(sha256a)
    sha256b = hashlib.sha256(binb).hexdigest()
    hmmmm = binascii.unhexlify(net_byte + sha256b[:8])
    final = base58.b58encode(hmmmm)
    return(final.decode())


# FIXME don't sys.exit from TUI
# function to unlock ALL lockunspent UTXOs
def unlockunspent(rpc_connection):
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


# iterate addresses list, construct dictionary,
# with amount as value for each address
def sendmany64(rpc_connection, amount):
    addresses_dict = {}
    with open('list.json') as key_list:
        json_data = json.load(key_list)
        for i in json_data:
            address = i[3]
            addresses_dict[address] = amount

    # make rpc call, issue transaction
    sendmany_result = rpc_connection.sendmany("", addresses_dict, 0)
    return(sendmany_result)

# function to do sendmany64 UTXOS times, locking all UTXOs except change
def sendmanyloop(rpc_connection, amount, utxos):
    txid_list = []
    for i in range(int(utxos)):
        sendmany64_txid = sendmany64(rpc_connection, amount)
        txid_list.append(sendmany64_txid)
        getrawtx_result = rpc_connection.getrawtransaction(sendmany64_txid, 1)
        lockunspent_list = []
        # find change output, lock all other outputs
        for vout in getrawtx_result['vout']:
            if vout['value'] != float(amount):
                change_output = vout['n']
            else:
                output_dict = {
                    "txid": sendmany64_txid,
                    "vout": vout['n']
                    }
                lockunspent_list.append(output_dict)
        lockunspent_result = rpc_connection.lockunspent(False, lockunspent_list)
    return(txid_list)

def sendmany64_TUI(rpc_connection):
    balance = float(rpc_connection.getbalance())
    print('Balance: ' + str(balance))

    #AMOUNT = input("Please specify the size of UTXOs: ")
    AMOUNT = user_input('Please specify the size of UTXOs: ', int)
    if AMOUNT == 'exit':
        return(0)
    
    if float(AMOUNT) < float(1):
        print('Cant stake coin amounts less than 1 coin, try again.')
        return(0)
    UTXOS = user_input("Please specify the amount of UTXOs to send to each segid: ", int)
    if UTXOS == 'exit':
        return(0)

    total = float(AMOUNT) * int(UTXOS) * 64
    print('Total amount: ' + str(total))
    if total > balance:
        print('Total sending is ' + str(total-balance) + ' more than your balance. Try again.')
        segidTotal = balance / 64
        print('Total avalible per segid is: ' + str(segidTotal))
        return(0)

    sendmanyloop_result = sendmanyloop(rpc_connection, AMOUNT, UTXOS)
    # unlock all locked utxos
    unlockunspent(rpc_connection)
    for i in sendmanyloop_result:
        print(i)
    print('Success!')

# function to do sendmany64 UTXOS times, locking all UTXOs except change
def RNDsendmanyloop(rpc_connection, amounts):
    txid_list = []
    for amount in amounts:
        sendmany64_txid = sendmany64(rpc_connection, amount)
        txid_list.append(sendmany64_txid)
        getrawtx_result = rpc_connection.getrawtransaction(sendmany64_txid, 1)
        lockunspent_list = []
        # find change output, lock all other outputs
        for vout in getrawtx_result['vout']:
            if vout['value'] != float(amount):
                change_output = vout['n']
            else:
                output_dict = {
                    "txid": sendmany64_txid,
                    "vout": vout['n']
                    }
                lockunspent_list.append(output_dict)
        lockunspent_result = rpc_connection.lockunspent(False, lockunspent_list)
    return(txid_list)

def RNDsendmany_TUI(rpc_connection):

    try:
        balance = float(rpc_connection.getbalance())
    except Exception as e:
        print(e)
        return(0)

    print('Balance: ' + str(balance))

    while True:
        UTXOS = int(input("Please specify the amount of UTXOs to send to each segid: "))
        if UTXOS < 3:
            print('Must have more than 3 utxos per segid, try again.')
            continue
        TUTXOS = UTXOS * 64
        print('Total number of UTXOs: ' + str(TUTXOS))
        average = float(balance) / int(TUTXOS)
        print('Average utxo size: ' + str(average))
        variance = float(input('Enter percentage of variance: '))
        minsize = round(float(average) * (1-(variance/100)),2)
        if minsize < 1:
            print('Cant stake coin amounts less than 1 coin, try again.')
            continue
        maxsize = round(average + float(average) * (variance/100),2)
        print('Min size: ' + str(minsize))
        print('Max size: ' + str(maxsize))
        ret = input('Are you happy with these? ').lower()
        if ret.startswith('y'):
            break

    total = 0
    totalamnt = 0
    AMOUNTS = []
    finished = False

    while finished == False:
        for i in range(UTXOS):
            amnt = round(random.uniform(minsize,maxsize),2)
            totalamnt += amnt * 64
            AMOUNTS.append(amnt)
            if totalamnt > balance-0.1:
                totalamnt = 0
                AMOUNTS.clear()
                break
        if totalamnt > balance-2:
            finished = True

    sendmanyloop_result = RNDsendmanyloop(rpc_connection, AMOUNTS)
    # unlock all locked utxos
    unlockunspent(rpc_connection)
    for i in sendmanyloop_result:
        print(i)
    print('Success!')

def genaddresses(rpc_connection): # FIXME don't print in start script
    if os.path.isfile("list.json"):
        print('Already have list.json, move it if you would like to '
              'generate another set.You can use importlist.py script to import'
              ' the already existing list.py to a given chain.')
        return(1)
    
    # fill a list of sigids with matching segid address data
    segids = {}
    while len(segids.keys()) < 64:
        genvaldump_result = genvaldump(rpc_connection)
        segid = genvaldump_result[0]
        if segid in segids:
            pass
        else:
            segids[segid] = genvaldump_result

    # convert dictionary to array
    segids_array = []
    for position in range(64):
        segids_array.append(segids[position])

    # save output to list.py
    print('Success! list.json created. '
          'THIS FILE CONTAINS PRIVATE KEYS. KEEP IT SAFE.')
    f = open("list.json", "w+")
    f.write(json.dumps(segids_array))

# FIXME make this rescan only on 64th import
# import list.json to chain 
def import_list(rpc_connection):
    if not os.path.isfile("list.json"):
        print('No list.json file present. Use genaddresses.py script to generate one.')
        return(0)

    with open('list.json') as key_list:
        json_data = json.load(key_list)
        for i in json_data:
            print(i[3])
            rpc_connection.importprivkey(i[2])
    print('Success!')
    
def extract_segid(_segid,unspents):
    ret = []
    for unspent in unspents:
        if unspent['segid'] == _segid:
            unspent['amount'] = float(unspent['amount'])
            ret.append(unspent)
    return(ret)

def withdraw_TUI(rpc_connection):

    def unlockunspent2():
        try:
            listlockunspent_result = rpc_connection.listlockunspent()
        except Exception as e:
            print(e)
            withdraw_TUI(rpc_connection)
        unlock_list = []
        for i in listlockunspent_result:
            unlock_list.append(i)
        try:
            lockunspent_result = rpc_connection.lockunspent(True, unlock_list)
        except Exception as e:
            print(e)
            withdraw_TUI(rpc_connection)
        return(lockunspent_result)

    balance = float(rpc_connection.getbalance())
    print('Balance: ' + str(balance))

    address = input('Please specify address to withdraw to: ')
    try:
        address_check = addr_convert('3c', address)
    except Exception as e:
        print('invalid address:', str(e) + '\n')
        withdraw_TUI(rpc_connection)

    if address_check != address:
        print('Wrong address format, must use an R address')
        withdraw_TUI(rpc_connection)
    
    user_input = input("Please specify the percentage of balance to lock: ")
    try:
        PERC = int(user_input)
    except:
        print('Error: must be whole number')
        withdraw_TUI(rpc_connection)
    
    if PERC < 1:
        print('Error: Cant lock 0%.')
        withdraw_TUI(rpc_connection)

    # get listunspent
    try:        
        listunspent_result = rpc_connection.listunspent()
    except Exception as e:
        print(e)
        return(0)

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
        print(e)
        return(0)
    totalbalance = 0
    for unspent in listunspent_result:
        totalbalance = float(totalbalance) + float(unspent['amount'])

    balance = rpc_connection.getbalance()
    if totalbalance == balance:
        print('Balance available to send: ' + str(totalbalance))
    else:
        print('Balance available to send: ' + str(totalbalance))
        
    print('Balance available to send: ' + str(totalbalance))
        
    amount = float(input('Amount? '))
    if amount < 0 or amount > totalbalance:
        unlockunspent2()
        print('Too poor!')
        return(0)
        
    print('Sending ' + str(amount) + ' to ' + address)
    ret = input('Are you happy with these? ').lower()
    if ret.startswith('n'):
        unlockunspent2()
        print('You are not happy?')
        return(0)

    # send coins.
    txid_result = rpc_connection.sendtoaddress(address, amount)

    # unlock all locked utxos
    unlockunspent2()
    print('Success: ' + txid_result)

def startchain(rpc_connection):
    def blockcount():
        while True:
            getinfo_result = rpc_connection.getinfo()
            if getinfo_result['blocks'] > 1:
                rpc_connection.setgenerate(False)
                return(0)

    getinfo_result = rpc_connection.getinfo()

    if getinfo_result['blocks'] != 0:
        print('must be used on a new exiting')
        return(0)

    peers = rpc_connection.getpeerinfo()
    if not peers:
        print('No peers found, please connect your node to at least one other peer.')
        return(0)

    if 'eras' in getinfo_result:
        print('This script is incompatible with ac_eras chains. Please use genaddresses then RNDsendmany after block 100 instead.')
        return(0)

    def sendtoaddress(rpc_connection):
        address = input("Please specify address to withdraw coins to. It must not be owned by this node: ")
        try:
            address_check = addr_convert('3c', address)
        except Exception as e:
            print('invalid address:', str(e) + '\n')
            sendtoaddress(rpc_connection)
        if address_check != address:
            print('Wrong address format, must use an R address')
            sendtoaddress(rpc_connection)
        amount = input("Please specify the amount of coins to send: ")
        sendtoaddress_result = rpc_connection.sendtoaddress(address_check, amount)
        print(sendtoaddress_result)

    huh = input('Existing list.json found, would you like to import it?(y/n): ').lower()
    if huh.startswith('y'):
        import_list(rpc_connection)
    else:
        print('Must import a list.json')
        return(0)

    print('Mining blocks 1 and 2, please wait')
    rpc_connection.setgenerate(True, 2)

    blockcount()

    balance = rpc_connection.getbalance()
    if genaddresses(rpc_connection) == 1:
        ret = input('Would you like to stake the full premine?(y/n): ').lower()
        if not ret.startswith('y'):
            print('Balance: ' + str(rpc_connection.getbalance()))
            sendtoaddress(rpc_connection)
        RNDsendmany_TUI(rpc_connection)
        rpc_connection.setgenerate(True, 0)
        print('Your node has now begun staking. Ensure that at least one other node is mining.')
        return(0)

#####  ORACLES #####
oracletypes = [ 's', 'S', 'd', 'D', 'c', 't', 'i', 'l', 'h', 'Ihh']
def create_oracle(chain, name, description, oracletype):
    rpc_connection = def_credentials(chain)
    if oracletype not in oracletypes:
        errmsg = str(oracletype)+' is not a valid Oracle type. See https://developers.komodoplatform.com/basic-docs/cryptoconditions/cc-oracles.html#oraclescreate for details'
        print(colorize(errmsg, 'red'))
        exit(1)
    result = rpc_connection.oraclescreate(name, description, oracletype)
    oracleHex=result['hex']
    oracleResult=result['result']
    while oracleResult != 'success':
        result = rpc_connection.oraclescreate(name, description, oracletype)
        oracleHex=result['hex']
        oracleResult=result['result']
    oracletxid = rpc_connection.sendrawtransaction(oracleHex)
    while len(oracletxid) != 64:
        time.sleep(15)
        oracletxid = rpc_connection.sendrawtransaction(oracleHex)
    print(colorize("Oracle ["+oracletxid+"] created!", 'green'))
    return oracletxid


def register_oracle(chain, oracletxid, datafee):
    rpc_connection = def_credentials(chain)
    datafee=str(datafee)
    pubkey = rpc_connection.getinfo()['pubkey']
    rego = rpc_connection.oraclesregister(oracletxid, datafee)
    if rego['result'] == 'error':
        print(colorize(rego['error'], 'red'))
        exit(1)
    oracleHex=rego['hex']
    oracleResult=rego['result']
    while oracleResult != 'success':
        rego = rpc_connection.oraclesregister(oracletxid, datafee)
        oracleHex=rego['hex']
        oracleResult=rego['result']
    regotx = rpc_connection.sendrawtransaction(oracleHex)
    print(colorize('sending oracle registration tx', 'blue'))
    while len(regotx) != 64:
        time.sleep(15)
        regotx = rpc_connection.sendrawtransaction(oracleHex)  
        print(colorize('sending oracle registration tx', 'blue'))    
    memPool = str(rpc_connection.getrawmempool())
    while memPool.find(regotx) < 0:
        time.sleep(5)
        memPool = str(rpc_connection.getrawmempool())
    orcl_info = rpc_connection.oraclesinfo(oracletxid)
    reg_json=orcl_info['registered']
    while len(reg_json) < 1:
        print(colorize('waiting for oracle registration', 'blue'))
        time.sleep(15)
        orcl_info = rpc_connection.oraclesinfo(oracletxid)
        reg_json=orcl_info['registered']
    for reg_pub in reg_json:
        if reg_pub['publisher'] == pubkey:
            publisher=str(reg_pub['publisher'])
            funds=str(reg_pub['funds'])
            print(colorize("publisher ["+publisher+"] registered on oracle ["+oracletxid+"]!", 'green'))
    return publisher

def fund_oracle(chain, oracletxid, publisher, funds):
    rpc_connection = def_credentials(chain)
    pubkey = rpc_connection.getinfo()['pubkey']
    orcl_info = rpc_connection.oraclesinfo(oracletxid)
    reg_json=orcl_info['registered']
    for reg_pub in reg_json:
        if reg_pub['publisher'] == pubkey:
            exisingFunds=float(reg_pub['funds'])
    amount = float(funds)/10;
    sub_transactions = []
    for x in range(1,11):
        subtx = ''
        while len(subtx) != 64:
            print(colorize("Sending funds "+str(x)+"/10 to oracle", 'blue'))
            subHex = rpc_connection.oraclessubscribe(oracletxid, publisher, str(amount))['hex']
            subtx = rpc_connection.sendrawtransaction(subHex)
            time.sleep(5)
        sub_transactions.append(subtx)
        print(colorize("Funds "+str(x)+"/10 sent to oracle", 'blue'))
    while exisingFunds < 1:
        orcl_info = rpc_connection.oraclesinfo(oracletxid)
        reg_json=orcl_info['registered']
        for reg_pub in reg_json:
            if reg_pub['publisher'] == pubkey:
                exisingFunds=float(reg_pub['funds'])
        print(colorize("waiting for funds to appear on oracle",'blue'))
        time.sleep(15)
    print(colorize("Finished sending "+str(funds)+" to oracle.", 'green'))

def write2oracle(chain, oracletxid, message):
    rpc_connection = def_credentials(chain)
    rawhex = codecs.encode(message).hex()
    bytelen = int(len(rawhex) / int(2))
    hexlen = format(bytelen, 'x')
    if bytelen < 16:
        bigend = "000" + str(hexlen)
    elif bytelen < 256:
        bigend = "00" + str(hexlen)
    elif bytelen < 4096:
        bigend = "0" + str(hexlen)
    elif bytelen < 65536:
        bigend = str(hexlen)
    else:
        print("message too large, must be less than 65536 characters")
    lilend = bigend[2] + bigend[3] + bigend[0] + bigend[1]
    fullhex = lilend + rawhex
    oraclesdata_result = rpc_connection.oraclesdata(oracletxid, fullhex)
    result = oraclesdata_result['result']
    if result == 'error':
        print('ERROR:' + oraclesdata_result['error'] + ', try using oraclesregister if you have not already, and check the oracle is funded')
    else:
        rawtx = oraclesdata_result['hex']
        sendrawtransaction_result = rpc_connection.sendrawtransaction(rawtx)
    print(colorize("Message ["+message+"] written to oracle.", 'green'))
    return result

def read_oracle(chain, oracletxid, numrec):
    rpc_connection = def_credentials(chain)
    pubkey = rpc_connection.getinfo()['pubkey']
    orcl_info = rpc_connection.oraclesinfo(oracletxid)
    reg_json=orcl_info['registered']
    for reg_pub in reg_json:
        if reg_pub['publisher'] == pubkey:
            batonutxo=reg_pub['batontxid']
    if 'batonutxo' in locals():
        samples = rpc_connection.oraclessamples(oracletxid, batonutxo, str(numrec))
        print(colorize("ERROR: Oracle records retrieved.", 'red'))
        return samples['samples']
    else:
        print(colorize("ERROR: Oracle batonuto does not exist.", 'red'))





##############  TOKENS CC  #########################################################################

def create_tokens(chain, tokenname, tokendesc, tokensupply):
    rpc_connection = def_credentials(chain)
    result = rpc_connection.tokencreate(str(tokenname), str(tokensupply), str(tokendesc))
    if 'hex' in result.keys():
        tokentxid = rpc_connection.sendrawtransaction(result['hex'])
        print(colorize("Tokentxid ["+str(tokentxid)+"] created", 'green'))
        return tokentxid
    else:
        print(colorize("Tokentxid creation failed: ["+str(result)+"]", 'red'))
        exit(1)

def tokenbalance(chain, tokentxid, pubkey=""):
    rpc_connection = def_credentials(chain)
    if len(pubkey) == 66:
        result = rpc_connection.tokenbalance(str(tokentxid), str(pbkey))
    else:
        result = rpc_connection.tokenbalance(str(tokentxid))
    if 'result' in result.keys():
        if result['result'] == 'success':
            tokenaddress = result['CCaddress']
            balance = result['balance']
            print(colorize("Tokentxid ["+str(tokentxid)+"] address ["+str(tokenaddress)+"] has ["+str(balance)+"] balance", 'green'))
        else:
            print(colorize("Getting token balance failed: ["+str(result)+"]", 'red'))
            exit(1)
    else:
        print(colorize("Getting token balance failed: ["+str(result)+"]", 'red'))
        exit(1)



##############  GATEWAYS CC  #########################################################################

def bind_gateway(chain, tokentxid, oracletxid, tokenname, tokensupply, N, M, gatewayspubkey, pubtype, p2shtype, wiftype):
    rpc_connection = def_credentials(chain)
    if M != str(1) or N != str(1):
        print(colorize("Multisig gateway not yet supported in script, using 1 of 1.", 'red'))
        M = 1
        N = 1
    result = rpc_connection.gatewaysbind(tokentxid, oracletxid, tokenname, str(tokensupply), str(N), str(M), gatewayspubkey, str(pubtype), str(p2shtype), str(wiftype))
    if 'hex' in result.keys():
        bindtxid = rpc_connection.sendrawtransaction(result['hex'])
        print(colorize("Bindtxid ["+str(bindtxid)+"] created", 'green'))
        return bindtxid
    else:
        print(colorize("Bindtxid creation failed: ["+str(result)+"]", 'red'))
        exit(1)

def create_gateway():    
    chain = user_input('Enter asset-chain to create tokens on: ', str)
    tokenname = user_input('Enter token name: ', str)
    tokendesc = user_input('Enter token description: ', str)
    tokensupply = user_input('Enter token supply: ', str)
    tokentxid = create_tokens(chain, tokenname, tokendesc, tokensupply)
    oracletxid = create_oracle(chain, tokenname, 'blockheaders', 'Ihh')
    datafee = user_input('Enter oracle data fee (in satoshis): ', str)
    while int(datafee) < 10000:
        print(colorize("Datafee too low, set to 10k or more", 'blue'))
        datafee = user_input('Enter oracle data fee (in satoshis): ', str)
    oraclepublisher = register_oracle(chain, oracletxid, datafee)
    funds = user_input('Enter amount of funds to send to oracle: ', str)
    fund_oracle(chain, oracletxid, oraclepublisher, funds)
    N = user_input('Enter total number of gateways signatures: ', str)
    M = user_input('Enter number gateways signatures required to withdraw: ', str)
    tokensatsupply = 100000000*int(tokensupply)
    bindtx = bind_gateway(chain, tokentxid, oracletxid, tokenname, tokensatsupply, N, M, oraclepublisher, 60, 85, 188)
