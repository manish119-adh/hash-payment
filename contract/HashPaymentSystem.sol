// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.9;


// Smart contract is in simple terms programming the blockchain
// As with all programs it has it's state which is maintained as
// per the rules in the contract

// The contract is run decentralized by all the nodes in the chain and the state
// change is tracked by reading all the transactions in all the blocks from
// the beginning and making updates as new blocks are added to the chain
// new blocks are added by the miner



// A simple payment system which works by sender
// depositing the amount with some hash value and the claimand making
// claim with its preimage
contract OutContract {
    // A simple smart contract which receives a payment from a person along with an id
    // And refunds back to the person only if it comes with the preimage of the hash value
    // It was originally registered with

    mapping(bytes32 => Deposit) public deposits;

    struct Deposit{
        bytes32 hash;
        uint256 amount;
        address sender;
    }

    struct Struct1 {
        uint256 a;
        int64 b;
        string c;
        Struct2 params;
    }

    struct Struct2 {
        uint64 id;
        string c_;
        bytes d_;
        int[] e_;
    }

    bool reentrant_lock = false;

     modifier noReintrant {
        require (reentrant_lock == false, "Reentrant detected");
         reentrant_lock = true;
        _;
         reentrant_lock = false;
    }

    // Transfer amount from smart contract to some address
    function transferTo(uint256 amount, address addr) internal  {
        (bool sent, ) = payable(addr).call{value: amount}("");
        require(sent, "Fund transfer failed. Please try again");
    }

    //Make a new deposit with a hash value of some amount
    function newDeposit(bytes32 hsh) payable external noReintrant {
        Deposit storage deposit = deposits[hsh];
        deposit.hash = hsh;
        deposit.amount = msg.value;
        deposit.sender = msg.sender;

    }



    // Get the deposited amount
    // Our smart contract is capable of checking the hash value of given pre-image and
    // refuse the claim if not found
    // If fund transfer fails due to some reason, entire claim contract get rollbacked
    // So the record will still be on deposits
    function claim(bytes memory preimage) external noReintrant {
        bytes32 hsh = sha256(preimage);
        Deposit memory deposit = deposits[hsh];
        // require clause is used to check if particular condition is true
        // if it failed, entire transaction gets rollbacked, (never makes to blockchain)
        // So there is no state changes
        require(deposit.hash == hsh, "Deposit not found");
        delete deposits[hsh];
        transferTo(deposit.amount, msg.sender);

    }

    // Lookup the deposit for given hash.
    // Running this function only requires only reading the
    // chain without making any changes to it (i.e. adding any transaction)
    // Therefore it can be called from our python program
    // without creating transaction
    function checkout(bytes32 hash) public returns (Deposit memory){
        return deposits[hash];
    }


    function serialize(Struct1 calldata st1) public pure returns (bytes memory){
        return abi.encode(st1);
    }

    function deserialize(bytes calldata st2) public pure returns (Struct1 memory){
        return abi.decode(st2, (Struct1));
    }

    function hashStruct1(Struct1 calldata st1) public pure returns (bytes32){
        return keccak256(abi.encode(st1));
    }


}