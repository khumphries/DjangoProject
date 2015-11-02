__author__ = 'divya'

""" Description: Collection of functions that encrypt and decrypt   """
"""              files using ARC4 Encryption                        """
"""              standards                                          """

from Crypto.Cipher import ARC4
import ast

def encrypt_file(filename, key):
    """ Performs ARC4 Stream Cipher on inputted file using given symmetric key """
    crypter = ARC4.new(key)
    try:
        f = open(filename, 'rb')
    except:
        return False
    secret = f.read()
    encrypted = crypter.encrypt(secret)
    g = open(filename+".enc", 'wb')
    g.write(encrypted)
    return True

def decrypt_file(filename, key):
    """ Decrypts inputted file using given symmetric key """
    if filename[-4:] != ".enc":
        return False
    try:
        f = open(filename, 'rb')
    except:
        return False
    encryptd = f.read()
    obj = ARC4.new(key)
    decryptd = obj.decrypt(encryptd)
    g = open("DEC_" + filename[:-4], 'wb')
    g.write(decryptd)
    return True


