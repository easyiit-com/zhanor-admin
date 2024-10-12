import hashlib
from cryptography.fernet import Fernet

def hash_password(password, salt):
    """
    对密码进行加密处理，使用 MD5 算法，并添加盐值。
    
    :param password: 明文密码
    :param salt: 盐值，增加加密强度
    :return: 加密后的密码（MD5 哈希值）
    """
    return hashlib.md5((password + salt).encode('utf-8')).hexdigest()

def encrypt_words(key, words):
    """
    使用给定的密钥对文本进行加密，使用 Fernet 对称加密算法。
    
    :param key: 用于加密的密钥（Fernet 生成）
    :param words: 需要加密的明文文本
    :return: 加密后的文本，经过 Base64 编码
    """
    cipher = Fernet(key)
    encrypted_words = cipher.encrypt(words.encode('utf-8'))  # 加密文本
    return encrypted_words.decode('utf-8')  # 返回解码后的加密文本

def decrypt_words(key, encrypted_words):
    """
    使用给定的密钥对加密文本进行解密，恢复原文。
    
    :param key: 用于解密的密钥（必须与加密时使用的密钥相同）
    :param encrypted_words: 加密后的 Base64 编码文本
    :return: 解密后的明文文本
    """
    cipher = Fernet(key)
    decrypted_words = cipher.decrypt(encrypted_words.encode('utf-8'))  # 解密文本
    return decrypted_words.decode('utf-8')  # 返回解码后的明文文本
