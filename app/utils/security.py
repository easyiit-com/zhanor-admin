import hashlib

def hash_password(password, salt):
    return hashlib.md5((password + salt).encode('utf-8')).hexdigest()
