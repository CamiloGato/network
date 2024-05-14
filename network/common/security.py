import base64
from os import urandom

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def generate_keys() -> (RSAPrivateKey, RSAPublicKey):
    private_key: RSAPrivateKey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key: RSAPublicKey = private_key.public_key()
    return private_key, public_key


def serialize_key_private(key: RSAPrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )


def serialize_key_public(key: RSAPublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def generate_symmetric_key():
    return urandom(32)


def encrypt_message(message, key):
    iv = urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(message.encode() + encryptor.finalize())
    return base64.b64encode(iv + ct).decode()


def decrypt_message(enc_message, key):
    enc_message = base64.b64decode(enc_message.encode())
    iv = enc_message[:16]
    ct = enc_message[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    de_encryptor = cipher.decryptor()
    return (de_encryptor.update(ct) + de_encryptor.finalize()).decode()


def encrypt_symmetric_key(sym_key, public_key):
    encrypted_key = public_key.encrypt(
        sym_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted_key).decode()


def decrypt_symmetric_key(enc_sym_key, private_key):
    enc_sym_key = base64.b64decode(enc_sym_key.encode())
    sym_key = private_key.decrypt(
        enc_sym_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return sym_key
