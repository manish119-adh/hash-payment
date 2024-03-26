
from py_ecc.bn128 import curve_order,G1,G2


from Crypto.Hash import SHA512

from Crypto.Random import random

from main import Hashpayment
from py_ecc.bn128.bn128_curve import multiply as scalar_multiply
from py_ecc.bn128.bn128_curve import add as point_add
from py_ecc.bn128.bn128_curve import neg as point_neg
from py_ecc.bn128.bn128_pairing import pairing




# Even strangely, the bytes input to base in python implementation is same as bytes output in mcl
# implementation but the output from python implementation is different
# Something tells me the base should be same, but are being serialized differently
if __name__ == "__main__":
    order = curve_order
    g = G1
    g2 = G2
    x = random.randint(0,order)
    X = scalar_multiply(g,x)
    R = scalar_multiply(g2, random.randint(0,order))
    S_p = scalar_multiply(R, x)



    # Multiply check in contract


    # pair1 = pairing(S_p, g)
    # pair2 = pairing(R, X)
    # pair3 = pairing(R, g)
    # pair4 = pairing(S_p, X)
    #
    # chk1 = pair1 == pair2
    # chk2 = pair1 == pair3
    # chk3 = pair1 == pair4
    # chk4 = pair3 == pair4

    hdkj = 90

    def check_pairing_many(hp:Hashpayment, a_list, b, c_list, d):
        list_2_g1 = lambda lst_g1 : [(f[0].n,f[1].n) for f in lst_g1]
        _2g2 = lambda b_: (b_[0].coeffs[0].n,b_[0].coeffs[1].n,b_[1].coeffs[0].n,b_[1].coeffs[1].n)
        return hp.bn254_contract.functions.checkMultiplePairings(list_2_g1(a_list),_2g2(b),list_2_g1(c_list),_2g2(d)).call()




    def check_pairing(hp:Hashpayment, a, b, c, d):
        # check if e(a,b) = e(c,d) in smart contract
        # Must negate one of the points to check

        neg_c = point_neg(c)
        fcall = hp.bn254_contract.functions.checkPairing((a[0].n,a[1].n),(b[0].coeffs[0].n,b[0].coeffs[1].n,b[1].coeffs[0].n,b[1].coeffs[1].n),(neg_c[0].n,neg_c[1].n),(d[0].coeffs[0].n,d[0].coeffs[1].n,d[1].coeffs[0].n,d[1].coeffs[1].n))
        # fcall = hp.bn254_contract.functions.pairingProd3((a[0].n, a[1].n))

        return hp.make_transaction(fcall)

    def check_pairing_without_transaction(hp:Hashpayment, a, b, c, d):
        neg_c = point_neg(c)
        return hp.bn254_contract.functions.checkPairing((a[0].n, a[1].n), (
        b[0].coeffs[0].n, b[0].coeffs[1].n, b[1].coeffs[0].n, b[1].coeffs[1].n), (neg_c[0].n, neg_c[1].n), (
                                                         d[0].coeffs[0].n, d[0].coeffs[1].n, d[1].coeffs[0].n,
                                                         d[1].coeffs[1].n)).call()
        #


    # Check the same on smart contract
    contract = Hashpayment.new_deployment("http://127.0.0.1:8545", 1337, "0x5CE381742dbbD66eDBBAEA729c4ca2910513E783", "0xa49ef90f49f0e9ff05eff11ac50ff924ad08397b792542806455baf68d650ab0")
    r_list = [scalar_multiply(g, random.randint(0, order)) for _ in range(10)]
    X = scalar_multiply(g2, x)
    s_list = [scalar_multiply(r_, x) for r_ in r_list]
    succ = check_pairing_many(contract, s_list, g2, r_list, X)
    succ_ = check_pairing_many(contract, s_list[:5],g2,r_list[5:],X)
    S_p_ = contract.bn254_contract.functions.checkMultiplication((R[0].coeffs[0].n,R[0].coeffs[1].n,R[1].coeffs[0].n,R[1].coeffs[1].n),x).call()
    result = check_pairing(contract,g,S_p,X,R)
    print("First pairing passed")
    result = check_pairing(contract,g,S_p, g, R)
    print("Second pairing passed")
    ghhy = 89






# High level wrapper for point and point2 classes
# with access to their components as integers
