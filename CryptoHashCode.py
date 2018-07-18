
""" Encryption & Decryption of Message """


from Crypto import Random
from Crypto.Cipher import AES
import base64
from uuid import uuid4


unikey = "qwe@rty#uio$pasd"
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]


class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) ) 

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))


def get_decrypted_final_val(decodedmsg, first_len = 5, last_len = 4):
    return decodedmsg[first_len:len(decodedmsg)-last_len]


def toHashVal(val, first_len = 5, last_len = 4):
    fullid = "{0}{1}{2}".format(uuid4().hex[:first_len],val,uuid4().hex[:last_len])
    msg = AESCipher(unikey)
    return msg.encrypt(fullid)


def decryptHashVal(val, first_len = 5, last_len = 4):
    msg = AESCipher(unikey)
    dec = msg.decrypt(val)
    return get_decrypted_final_val(dec, first_len, last_len)




# ----------------- For Testing in Shell -----------------------------#


def test(id):
    
    print ("Initial Val : %s" %(id))

    fullid = "{0}{1}{2}".format(uuid4().hex[:6],id,uuid4().hex[:5])
    
    print ("Unique Key : %s" %(unikey))
    
    print ("Full ID : %s" %(fullid))

    msg = AESCipher(unikey)
    
    enc = msg.encrypt(fullid)
    
    print ("Encrypted Msg : %s" %(enc))
    
    dec = msg.decrypt(enc)
    
    print ("Decrypted Msg : %s" %(dec))
    
    final_id = get_decrypted_final_val(dec)
    
    print ("Final Value : %s" %(final_id))

    return " ---------------------  Done --------------------- "
    
# ----------------- For Testing in Shell -----------------------------#
    
