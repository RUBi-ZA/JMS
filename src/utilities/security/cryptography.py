from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

import random

class Cipher:
    
    @staticmethod
    def generate_key(length):
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYZ"
        chars = []
        for i in range(length):
            chars.append(random.choice(ALPHABET))
        return "".join(chars)
    
    
    @staticmethod
    def encrypt(key, text):
        salt_len = 16 - len(text) % 16
        salt = Cryptography.GenerateKey(salt_len)
        
        cipher = AES.new(key, AES.MODE_CBC, " is a 16 byte IV")
        encrypted = cipher.encrypt(text + salt)
        return salt, encrypted
        
    
    @staticmethod
    def decrypt(key, salt, encrypted):
        cipher = AES.new(key, AES.MODE_CBC, " is a 16 byte IV")
        decrypted = cipher.decrypt(encrypted)        
        decrypted = decrypted[:-len(salt)]        
        return decrypted     
        
        

class PubPvtKey:
    
    @staticmethod
    def generate_key_files(length=2048, directory="."):
        key = RSA.generate(length)
        
        pvt_key = key.exportKey()
        pub_key = key.publickey().exportKey()
        
        with open("%s/pvt.key" % directory, "w") as key_file:
            key_file.write(pvt_key)
        
        with open("%s/pub.key" % directory, "w") as key_file:
            key_file.write(pub_key)
                
    
    @staticmethod
    def encrypt(key, text):
        key = RSA.importKey(key)
        encrypted = key.publickey().encrypt(text, 32)[0]
        return encrypted
        
    
    @staticmethod
    def decrypt(key, encrypted):
        key = RSA.importKey(key)
        return key.decrypt(encrypted)
