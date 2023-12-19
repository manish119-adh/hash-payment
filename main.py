# solcx is python solidity compiler. It compiles solidity smart contracts into bytecode
# For deployment
import solcx
import web3
from solcx import install_solc, compile_standard, link_code
# web3 is pythom library to interact with ethereum blockchain
# It consists of all the works to connect to, deploy and run contracts on the  ethereum
# and also to monitor it and track correct chain state
from web3 import Web3
from web3.exceptions import ContractLogicError
from Crypto.Hash import SHA256


# In order to run this, we need to have local ethereum simulator called ganache installed
# we will use cli version of ganache called ganache-cli
# Ganache initializes with some addresses with balance 100 ether from the start
# Addresses are geenrated randomly at default, but we can make the whole process
# deterministic by using mnemonics

# Install ganache using "npm install ganache-cli"
# Run ganache with deterministaic addrress generation to match our hardcoded addresses using
#  ganache-cli -d -m "i elephant plane car tero bwaso no high meat psycho blackhole tired touko none ttyero"
# Alternatively you can use your own mnemonics which generate different addresses and replace
# The given hardcoded addresses with new addresses

class Hashpayment:

    def __init__(self, url, chainid, address, privatekey, contract=None, bncontract=None):
        self.chain = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 60}))
        self.chainid = chainid
        if contract is not None:
            # Contract if not None must be a tuple (abi, contract_address) representing a contract
            self.deployed_contract = self.chain.eth.contract(address=contract[1], abi=contract[0])
        else:
            self.deployed_contract = None

        if bncontract is not None:
            self.bn254_contract = self.chain.eth.contract(address=bncontract[1], abi=bncontract[0])
        else:
            self.bn254_contract = None
        self.address = address
        self.privatekey = privatekey
        pass



    def compile_contracts(self):
        # solc is the python solidity compiler. It must be installed by calling
        # set_solc_version to compile the contract
        # Install solc, it is required to use it to compile the contract
        install_solc("0.8.9")
        solcx.set_solc_version('0.8.9')
        # Compile the contract. To compile following inputs must be provided
        compiler_input = {
            'language': 'Solidity', # language
            'sources': {
                "HashPaymentSystem.sol": {'urls': ["contract/HashPaymentSystem.sol"]}, # Source files
                "BN254.sol":{'urls':["contract/bn254/BN254.sol"]},
                "Utils.sol":{'urls':["contract/bn254/Utils.sol"]},
                "PairingCheckContract.sol": {'urls': ["contract/bn254/PairingCheckContract.sol"]}

            },
            'settings': {  # What outputs we need. We are interested in abi and bytecode
                'outputSelection': {
                    '*': {
                        '*': ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"],
                    },
                    'def': {"*": ["abi", "evm.bytecode.opcodes"]},
                }
            }
        }
        compiled = compile_standard(compiler_input,
                                    allow_paths=["contract","contract/bn254"])
        self.raw_contract = compiled


    # After compiling it needs to be deployed. Deploying the contract
    # sometimes requires costructor parameters as defined in the constructor of the contract
    #Deploy contracts that are not already deployed
    def deploy_contract(self, abi, bin, *constructor_params):
        # Define the contract with bytecode and abi, create deployment transaction, sign it and run as others
        # This deploys the contract and runs the constructor
        CurveContract = self.chain.eth.contract(abi=abi, bytecode=bin)
        nonce = self.chain.eth.get_transaction_count(self.address)
        deploytransaction = CurveContract.constructor(*constructor_params).build_transaction(
            {"chainId": self.chainid, "from": self.address, "nonce": nonce,
             "gasPrice": self.chain.eth.gas_price})
        signedtran = self.chain.eth.account.sign_transaction(deploytransaction, self.privatekey)
        transent = self.chain.eth.send_raw_transaction(signedtran.rawTransaction)
        receipt = self.chain.eth.wait_for_transaction_receipt(transent)
        return receipt.contractAddress

    def deploy_contracts(self):
        # Deploy all contracts in our program. In this case it is just OutContract in HashPaymentSystem.sol
        # First extract abi and bytecode from our compiled contract
        # Deploy only those which are not already deployed
        def get_abi_and_binary(path, name):
            abi = self.raw_contract['contracts'][path][name]['abi']
            bin = self.raw_contract['contracts'][path][name]['evm']['bytecode']['object']
            return abi, bin
        if self.deployed_contract is None:
            (mainabi, mainbin) = get_abi_and_binary("HashPaymentSystem.sol", "OutContract")
            # Deploy it and set address of our contract to new deployed address
            contract_addr = self.deploy_contract(mainabi,mainbin)
            self.deployed_contract = self.chain.eth.contract(address=contract_addr, abi=mainabi)
        #Deploy the library and contract for BN254
        if self.bn254_contract is None:
            (utilabi, utilbin) = get_abi_and_binary("Utils.sol", "Utils")
            util_addr = self.deploy_contract(utilabi, utilbin)
            util_contract = self.chain.eth.contract(address=util_addr,abi=utilabi)
            (bnabi,bnbin) = get_abi_and_binary("BN254.sol","BN254")
            bn_addr = self.deploy_contract(bnabi,bnbin)
            (pairingabi, pairingbin) = get_abi_and_binary("PairingCheckContract.sol","PairingCheckContract")
            pairingbin = link_code(pairingbin,
                                   {"BN254.sol:BN254": bn_addr})

            pair_addr = self.deploy_contract(pairingabi, pairingbin)
            self.bn254_contract = self.chain.eth.contract(address=pair_addr,abi=pairingabi)

    @staticmethod
    def new_deployment(url, chainid, address, privatekey):
        # Build new Hashpayment object without contract
        # Then compile the contract and deploy it setting the deployed_contract to the newly deployed contract
        hashpayment = Hashpayment(url,chainid,address,privatekey)
        hashpayment.compile_contracts()
        hashpayment.deploy_contracts()
        return hashpayment


   # In order to call any function in the smart contract, you need to prepare
    # the transaction (except those which make no changes to the blockchain which does not
    # require creating transaction)
    def make_transaction(self, function_call, paid_amount=0):
        try:
            # Transaction number from the same address needs to be checked. It is unique
            # It can be obtained by get_transaction_count
            nonce = self.chain.eth.get_transaction_count(self.address)
            # To create transaction it requires chainId, the address, nonce and the amount to pay (if any)
            deploytransaction = function_call.build_transaction(
                {"chainId": self.chainid, "from": self.address, "nonce": nonce,
                 "gasPrice": self.chain.eth.gas_price, "value": paid_amount})
            # The transaction is signed using the private key
            signedtran = self.chain.eth.account.sign_transaction(deploytransaction, self.privatekey)
            # The transaction gives the bytecode represenattion called rawTransaction which is signed
            # and sent to blockchian
            transent = self.chain.eth.send_raw_transaction(signedtran.rawTransaction)
            receipt = self.chain.eth.wait_for_transaction_receipt(transent)
            # Transaction receipt details gas price paid and other details
            return receipt
        except BaseException as exp:
            raise exp




   # Call function to check amount and sender of given amount by calling smart contract function
    # checkout
    def checkout(self, hash):
        (hsh, amt, sender) = self.deployed_contract.functions.checkout(hash).call()
        return {"hash":hsh, "amount": amt, "sender":sender}

    # Call smart contract function newDeposit to deposit the amount
    # Send payment of given amount (in wei) registered as hashval
    def new_deposit(self, hashval, amount):
        # Convert deposited amount to wei, which is the actual value
        # that is used by chain (as integer). The input is in ether
        # wei is the smallest indivisible amount
        # 1 ether = 1000000000000000000 wei
        amount = Web3.to_wei(amount, "ether")
        fcall = self.deployed_contract.functions.newDeposit(hashval)
        return self.make_transaction(fcall, paid_amount=amount)

    # Call smart contract function claim to claim deposited amount
    # Claim from blockchain
    def claim(self, preimage):
        fcall = self.deployed_contract.functions.claim(preimage)
        return self.make_transaction(fcall)

    # Check the balance (in wei) of your address using the get_balance method
    def check_balance(self):
        return self.chain.eth.get_balance(self.address, "latest")



    # There are two types of function call here.
    # checkout is done using call() construct of a contract function. call() is often used
    # with function that does not change blockchain scope
    # It can even be done locally without even actually interacting with the blockchain if you already
    # have all the blocks. Overall call() never makes changes to blockchain state
    # Any interaction is limited to ensuring that you have the latest blocks
    # However make_transaction actually sends a new "blockchain transaction" to the blockchain and makes
    # changes to the state. It requires paying the miners to do the work
    # new_deposit and claim are two functions that require it because it makes changes to blockchain state



    # In ethereum each contract also has an address which is the address we get at deployment. Each
    # contract then also has a balance, which it can hold by receiving payments from the buyers
    # Each contract then can transfer fund to other addresses based on rules in the contract
    # Here in this case, the contract automatically pays those who claim the payment with the valid pre-image


if __name__ == "__main__":
    # Create someone to deposit the payment
    # Because the contract is not deployed yet, the depositor is also responsible for deploying
    # the contract before any deposit is made
    depositor = Hashpayment.new_deployment("http://127.0.0.1:8545", 1337, "0x5CE381742dbbD66eDBBAEA729c4ca2910513E783", "0xa49ef90f49f0e9ff05eff11ac50ff924ad08397b792542806455baf68d650ab0")
    # Create a receiver after it deposits the payment
    receiver = Hashpayment("http://127.0.0.1:8545",1337,"0xC2960602b1437c7B67D5B9Ebe03278a04300F59f", "0x4f2b3c09f93653c9282af0e2f01ec3c9c0c4760d7e490444eb41bd6b98efbd86",(depositor.deployed_contract.abi,depositor.deployed_contract.address))
    deposit_bytes = b'thisismytestbuyeskeywordforall'
    deposit_hash = SHA256.new(deposit_bytes).digest()
    print(f"First balance, depositor = {depositor.check_balance()} receiver = {receiver.check_balance()}")
    depositor.new_deposit(deposit_hash, 20)
    print(f"After deposit, depositor = {depositor.check_balance()} receiver = {receiver.check_balance()}")
    # Receiver tries to obtain payment
    # with wrong hash
    try:
        receiver.claim(b'8398bdcbi2edd')
    except ContractLogicError as err:
        print(f"Claim failed:: {err.message}")
    print(f"Claim 1, depositor = {depositor.check_balance()} receiver = {receiver.check_balance()}")
    # With correst hash, claim
    try:
        receiver.claim(deposit_bytes)
    except ContractLogicError as err:
        print(f"Claim failed:: {err.message}")
    print(f"Claim 2, depositor = {depositor.check_balance()} receiver = {receiver.check_balance()}")
    # Try to claim same balance twice
    try:
        receiver.claim(deposit_bytes)
    except ContractLogicError as err:
        print(f"Claim failed:: {err.message}")
    print(f"Claim 3, depositor = {depositor.check_balance()} receiver = {receiver.check_balance()}")
    jhsj = 9

    # The contract has depositor (who also deployed the contract and therefore is the owner)
    # depositing 20 ethers and receiver claiming it. Three claims are made
    # Claim 1 with wrong pre image causing payment to be refused
    # Claim 2 with correct pre-image, payment succeeds
    # Claim 3 with correct pre-image but attempt at double claim
    # which also fails











