import socket
import struct
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


KEY = b"pixelcodepixelco"
AUTH = b"54643474-a769-417e-9a71-8be2f604ffe9"


def pkcs7_unpad(data):
    p = data[-1]
    return data[:-p]


def pkcs7_pad(data):
    p = 16 - (len(data) % 16)
    return data + bytes([p]) * p


def decrypt_packet(raw):
    iv = raw[:16]
    ct = raw[16:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    return pkcs7_unpad(pt)


def encrypt_packet(plaintext):
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pkcs7_pad(plaintext))
    payload = iv + ct

    return struct.pack(">I", len(payload)) + payload


def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def handle_client(conn):
    header = recv_exact(conn, 4)
    if not header:
        return

    length = struct.unpack(">I", header)[0]

    encrypted = recv_exact(conn, length)
    if not encrypted:
        return

    auth_message = decrypt_packet(encrypted)

    if auth_message == AUTH:
        conn.sendall(encrypt_packet(b"ping"))
        conn.sendall(encrypt_packet(b"clctf{p1X3L_c0D3_C2_1n_Y0u7Ub3}"))


def main():
    host = "0.0.0.0"
    port = 12732

    server = socket.socket()
    server.bind((host, port))
    server.listen(1)

    while True:
        conn, addr = server.accept()
        handle_client(conn)
        conn.close()


if __name__ == "__main__":
    main()