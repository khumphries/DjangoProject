from Crypto.Cipher import ARC4

def encrypt_msg(msg, key=None):
    """ Performs ARC4 Stream Cipher on msg using given symmetric key """
    if key == None:
        key = "14384624708653"
    crypter = ARC4.new(key)
    encrypted = crypter.encrypt(msg)
    return str(encrypted)

def decrypt_msg(msg, key=None):
    if key == None:
        key = "14384624708653"
    crypter = ARC4.new(key)
    msg = msg.encode('utf-8')[2:-1]
    #print(msg, type(msg))
    msg = msg.decode('unicode-escape').encode('ISO-8859-1')
    #print(msg, type(msg))
    #print(msg.decode('utf-8').encode('unicode-escape'))
    decrypted = crypter.decrypt(msg)
    return decrypted.decode('utf-8')


#msg = "hello"
#enc = encrypt_msg(msg, "123456789")
#print(decrypt_msg(enc, "123456789"))