
from py_ecc import bn128


from Crypto.Hash import SHA512

from Crypto.Random import random




# Even strangely, the bytes input to base in python implementation is same as bytes output in mcl
# implementation but the output from python implementation is different
# Something tells me the base should be same, but are being serialized differently
if __name__ == "__main__":

    def check_pairing(hp:Hashpayment, a: ECp, b: ECp2, c: ECp, d:ECp2):
        # check if e(a,b) = e(c,d) in smart contract
        # Must negate one of the points to check

        neg_c = -c
        fcall = hp.bn254_contract.functions.pairingProd2((a.x.x,a.y.x),(b.x.a.x,b.x.b.x,b.y.a.x,b.y.b.x),(neg_c.x.x,neg_c.y.x),(d.x.a.x,d.x.b.x,d.y.a.x,d.y.b.x))
        return hp.make_transaction(fcall)

    # Check the same on smart contract
    contract = Hashpayment.new_deployment("http://127.0.0.1:8545", 1337, "0x5CE381742dbbD66eDBBAEA729c4ca2910513E783", "0xa49ef90f49f0e9ff05eff11ac50ff924ad08397b792542806455baf68d650ab0")
    check_pairing(contract,g,S_p,X,R)
    print("First pairing passed")
    check_pairing(contract,bn254.scalar.from_int(2)*g,R,X, S_p)

# High level wrapper for point and point2 classes
# with access to their components as integers
