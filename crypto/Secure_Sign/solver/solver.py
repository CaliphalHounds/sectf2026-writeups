import requests
import sys

from base64 import b64encode

from Crypto.Hash import SHA256
from Crypto.PublicKey.ECC import EccKey
from Crypto.Signature import DSS
from Crypto.Util.asn1 import DerSequence


BASE_URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:7000'


email, password = f'asdf@asdf', 'asdffdsa'

session = requests.Session()
session.post(f'{BASE_URL}/api/register', json={'email': email, 'password': password})
session.post(f'{BASE_URL}/api/login', json={'email': email, 'password': password})

files = [{'filename': '', 'content': ''} for _ in range(2 ** (16 - 4) + 1)]
files[0]['content'] = b64encode(b'a').decode()

data = session.post(f'{BASE_URL}/api/sign', json={'files': files}).json()

public_key = data['public_key']
signatures = [data['results'][i]['signature'] for i in range(len(data['results']))]

r1, s1 = DerSequence().decode(bytes.fromhex(signatures[0]))
r2, s2 = DerSequence().decode(bytes.fromhex(signatures[-1]))
assert r1 == r2 and s1 != s2

h1 = int(SHA256.new(b'a').hexdigest(), 16)
h2 = int(SHA256.new(b'').hexdigest(), 16)

# s1 * k = h1 + r1 * d
# s2 * k = h2 + r2 * d

# k = (h1 + r1 * d) * s1^-1
# k = (h2 + r2 * d) * s2^-1

# (h1 + r1 * d) * s2 = (h2 + r2 * d) * s1

# d = (h1 * s2 - h2 * s1) * (r2 * s1 - r1 * s2)^-1

n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
d = (h1 * s2 - h2 * s1) * pow(r2 * s1 - r1 * s2, -1, n) % n
Q = EccKey(curve='P-256', d=d).public_key().pointQ

if f'04{int(Q.x):064x}{int(Q.y):064x}' != public_key:
    exit(1)

signature = DSS.new(EccKey(curve='P-256', d=d), mode='fips-186-3', encoding='der').sign(SHA256.new(bytes.fromhex(public_key)))

data = session.post(f'{BASE_URL}/api/verify', files={
    'document': ('public_key', bytes.fromhex(public_key)),
    'signature_file': ('signature', signature.hex()),
}).json()

if data.get('valid') and (flag := data.get('flag')):
    print(flag)
else:
    exit(1)
