// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import {BN254} from "./BN254.sol";
import {BN256G2} from "./BN256G2.sol";
contract PairingCheckContract {
    constructor(){

    }

    uint64 public countdone =0;

    function checkPairing(BN254.G1Point memory a1, BN254.G2Point memory a2, BN254.G1Point memory b1, BN254.G2Point memory b2) external {
        bool pairing = BN254.pairingProd2(a1,a2,b1,b2);
        require(pairing,"Pairing mismatch");
        countdone = countdone + 1;

    }

    function checkMultiplication(BN254.G2Point memory g1, BN254.ScalarField s)public view returns (BN254.G2Point memory){
       (uint256 x0, uint256 x1, uint256 y0, uint256 y1) = BN256G2.ECTwistMul(BN254.ScalarField.unwrap(s),
        BN254.BaseField.unwrap(g1.x0),BN254.BaseField.unwrap(g1.x1),BN254.BaseField.unwrap(g1.y0),BN254.BaseField.unwrap(g1.y1));
        return BN254.G2Point(BN254.BaseField.wrap(x0),BN254.BaseField.wrap(x1),BN254.BaseField.wrap(y0),BN254.BaseField.wrap(y1));
    }

    function checkAddition(BN254.G2Point memory g1, BN254.G2Point memory g2)public view returns (BN254.G2Point memory){
       (uint256 x0, uint256 x1, uint256 y0, uint256 y1) = BN256G2.ECTwistAdd(
        BN254.BaseField.unwrap(g1.x0),BN254.BaseField.unwrap(g1.x1),BN254.BaseField.unwrap(g1.y0),BN254.BaseField.unwrap(g1.y1),
        BN254.BaseField.unwrap(g2.x0),BN254.BaseField.unwrap(g2.x1),BN254.BaseField.unwrap(g2.y0),BN254.BaseField.unwrap(g2.y1));
        return BN254.G2Point(BN254.BaseField.wrap(x0),BN254.BaseField.wrap(x1),BN254.BaseField.wrap(y0),BN254.BaseField.wrap(y1));
    }

     // Check if e(si,g2,ri,x) holds for all si,ri in zip(s_lst,r_lst)
    // Since pairing is expensive operation it is done by checking one single pairing using
    // a mathematical trick below
    function checkMultiplePairings(BN254.G1Point[] memory s_lst, BN254.G2Point memory g2, BN254.G1Point[] memory r_lst, BN254.G2Point memory x) public view returns (bool){
        bytes32 keccakpack = keccak256(abi.encode(s_lst, r_lst));
        require(s_lst.length == r_lst.length, "Lengths must be equal");
      BN254.G1Point memory r_sum = BN254.infinity();
      BN254.G1Point memory s_sum = BN254.infinity();
      for (uint256 i=0;i<r_lst.length;i++){
          BN254.ScalarField ai = BN254.ScalarField.wrap((uint256(keccak256(abi.encodePacked(keccakpack, i)))) % BN254.R_MOD);
          r_sum = BN254.add(r_sum, BN254.scalarMul(r_lst[i], ai));
          s_sum = BN254.add(s_sum, BN254.scalarMul(s_lst[i], ai));
       }
       BN254.G1Point memory r_sum_neg = BN254.negate(r_sum);
       bool paired = BN254.pairingProd2(s_sum,g2,r_sum_neg,x);
        return paired;
    }
}
