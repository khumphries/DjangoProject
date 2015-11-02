import Crypter
from Crypto import Random
from Crypto.PublicKey import RSA
import ast
from Crypto.Cipher import ARC4


if __name__ == "__main__":
    """ Testing for above encryption/decryption functions """
    print(Crypter.encrypt_file('Diff.png', "14384624708653"))
    print(Crypter.decrypt_file('Diff.png.enc', "14384624708653"))
    
