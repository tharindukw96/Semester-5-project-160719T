import web3 
web3.eth.getBlock(12345)
w3 = Web3(Web3.IPCProvider())
a= w3.toChecksumAddress('0xd3cda913deb6f67967b99d67acdfa1712c293601')
print(w3.eth.getBalance(a))