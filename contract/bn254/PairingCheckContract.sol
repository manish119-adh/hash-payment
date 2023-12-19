// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import {BN254} from "./BN254.sol";
contract PairingCheckContract {
    constructor(){

    }

    uint64 public countdone =0;

    function checkPairing(BN254.G1Point memory a1, BN254.G2Point memory a2, BN254.G1Point memory b1, BN254.G2Point memory b2) external {
        bool pairing = BN254.pairingProd2(a1,a2,b1,b2);
        require(pairing,"Pairing mismatch");
        countdone = countdone + 1;

    }
}
