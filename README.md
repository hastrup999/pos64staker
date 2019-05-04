## Dependencies
```shell
sudo apt-get install python3-dev
sudo apt-get install python3 libgnutls28-dev libssl-dev
sudo apt-get install python3-pip
pip3 install setuptools
pip3 install wheel
pip3 install base58 slick-bitcoinrpc
```

## Payments CC Game 

- Object of the game is to receive as many airdropped coins as possible.
- Every 1440 blocks a snapshot is triggered on the chain. The top 3999 address by balance from highest to lowest is added to a list.
- The snapshot will rewind back to the last notarized height. 
- The block hash of this block is used to generate 2 numbers, one below 50 and one above 50. 
- These numbers represent a percentage. For example, 20-80 means that the top 20% are paid nothing and the bottom 20% are paid nothing.
- The entire airdrop is shared equally between all address inside the range. 
- A basic strategy is to simply create X address and spread your balance out over these, trying to keep most of them in the middle of the rich list, as this is the most likely to be airdropped multiple times. 
- Anyone can release the coins 1460 blocks after they are created. This means that at block 2900, `paymentsrelease` RPC can be run by any person. You can unlock anything over 5 Million coins. Any remaining coins, will be locked for 1460 blocks. So to release them, the next snapshot will have already happened changing the range of address. 
- The idea is to release the funds as quickly as possible to your advantage before somebody else. 
- After a few days, if only half has been released each time, the amount possible to release will be increased, there is no maximum release. The only constrints are is that it has been 1460 blocks since the funding arrived (either from coinbase payment each 1440 blocks, or change from a previous release.) and that the minimum released is 5 Million coins.
- Example: I release 5M coins at block 2901, 5M coins (-txfee) return to the payments fund, and not able to be released again until block 4361. A thing to consider here is because of txfees, the 5M would actually be locked until some other amount is sent, either by someone funding the plan with `paymentsfund` 1460 blocks earlier, or by the 10M coinbase payment, or change from another release. 

## Some scripts 

You can generate addresses with `genaddresses.py` 
- It simply asks for input, for chain name: CFEKPAY and the amount of address to make. 

You can then send these with `splittoaddress.py`
- Hardcoded to CFEKPAY, gets balance of wallet automatically. 
- Asks for vairance and then generates a `sendmany` that sends to your list of address. 
- Variance is a min and max size by percentage. Just answer `y` to `are you happy with these?` to send it. or `n`to try a diffrent percentageof variance.
