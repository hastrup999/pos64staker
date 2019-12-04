# pos64 Staking Contest & Bug Hunt - 5 Dec 2019

KMDLabs is holding a testing and bug-hunting competition this Friday, December 6, at 12:00 UTC. The competition will test and debug a new Proof of Stake (PoS) algorithm that will be activated in the Komodo ecosystem on December 20, 2019. 

Shortly after 12:00 UTC on December 6, the LABS team will create a new test chain that uses the new PoS algorithm. The coins will be airdropped to all registered participants. Then the participants will start staking the test coins to test the new algorithm and accumulate as many block rewards as possible. The users with the highest test coin balances at the end of the testing period will receive awards. Additional bounties will be distributed to users who find bugs.

It’s recommended that participants use a Linux machine and are comfortable with GitHub.

## Contest Details

If 20 or more users participate, the LABS team will give away at least 1500 KMD and 10,000 LABS in prizes! 

1st place - 333 KMD and 7777 LABS

2nd place - 200 KMD and 2000 LABS

3rd place - 1000 LABS

Additional Bug Bounties - up to 1000 KMD and 10,000 LABS

If fewer than 20 people participate in the LABS competition, there will still be prizes but they will be half of the amounts listed above. Sign up now to make sure that the full prize pool is unlocked!

If you have any questions or need help getting started, please ask the [#kmd-labs Discord channel](https://discord.gg/593akQW).

### Dependencies

sudo apt-get install python3 libgnutls28-dev libssl-dev

sudo apt-get install python3-pip

pip3 install setuptools

pip3 install wheel

pip3 install base58 slick-bitcoinrpc python-bitcoinlib

### Sign up

Fork pos64staker

Clone your fork

```
git checkout pos64test
```

Copy komodod to ~/pos64staker/komodod

run ```
entercomp.py
```
```
git add participants.json
```
```
git commit -m 'anything'
```
```
git push origin pos64test
```
PR those changes back to the repo

Keep **PRIVATE.json**, it has all the keys you need for the competition. **THIS FILE CONTAINS PRIVATE KEYS. KEEP IT SAFE.**
