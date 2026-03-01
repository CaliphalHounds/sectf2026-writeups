from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from pwn import *
import struct

KEY = b"pixelcodepixelco"
AUTH = b"54643474-a769-417e-9a71-8be2f604ffe9"


def pkcs7_unpad(data):
    return data[:-data[-1]]


def pkcs7_pad(data):
    p = 16 - (len(data) % 16)
    return data + bytes([p]) * p


def encrypt_packet(plaintext):
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pkcs7_pad(plaintext))
    payload = iv + ct

    return struct.pack(">I", len(payload)) + payload


def decrypt_packet(raw):
    iv = raw[:16]
    ct = raw[16:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    return pkcs7_unpad(pt)


def recv_packet(r):
    header = r.recvn(4)
    length = struct.unpack(">I", header)[0]

    data = r.recvn(length)
    return data


r = remote("185.234.69.58", 12732)

r.send(encrypt_packet(AUTH))

packet1 = recv_packet(r)
packet2 = recv_packet(r)

print(decrypt_packet(packet1))
print(decrypt_packet(packet2))