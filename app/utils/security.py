import hashlib
from cryptography.fernet import Fernet

def hash_password(password, salt):
    return hashlib.md5((password + salt).encode('utf-8')).hexdigest()

def encrypt_words(key,words):
    """加密文本"""
    cipher = Fernet(key)
    encrypted_words = cipher.encrypt(words.encode())
    return encrypted_words.decode()

def decrypt_words(key,encrypted_words):
    """解密文本"""
    cipher = Fernet(key)
    decrypted_words = cipher.decrypt(encrypted_words.encode())
    return decrypted_words.decode()
