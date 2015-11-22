from Crypto.Cipher import ARC4

def encrypt_msg(msg, key=None):
    """ Performs ARC4 Stream Cipher on msg using given symmetric key """
    if key == None:
        key = "14384624708653"
    crypter = ARC4.new(key)
    encrypted = crypter.encrypt(msg)
    return encrypted

def decrypt_msg(msg, key=None):
    if key == None:
        key = "14384624708653"
    crypter = ARC4.new(key)
    decrypted = crypter.decrypt(msg)
    return decrypted