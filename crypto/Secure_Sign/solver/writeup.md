# Secure Sign

> CTF Track Securiters - RootedCON 2026

> 27/02/2026 18:00 CEST - 01/03/2026 18:00 CEST

* Categoría: Criptografía
* Autor: 7Rocky
* Dificultad: ★★
* Etiquetas: ECDSA, LCG

## Descripción

Las librerías criptográficas de ECDSA en Go tienen una API muy rara, así que he creado mi propia implementación de la firma

## Resolución

Se presenta una aplicación web para firmar documentos digitalmente y verificar documentos firmados. El backend está escrito en Go. Al ser un reto de crypto, hay que centrarse en las vulnerabilidades de criptografía, por lo que el archivo relevante es `handlers/crypto.go`.

Las firmas utilizan ECDSA, y este es el código que la genera:

```go
hash := sha256.Sum256(fileBytes)
priv := utils.GetPrivateKey()
N := priv.Params().N

buf := make([]byte, 32)
reader.Read(buf)
k := new(big.Int).SetBytes(buf)
k.Mod(k, N)

kGx, _ := priv.Curve.ScalarBaseMult(k.Bytes())
r := new(big.Int).Mod(kGx, N)
s := new(big.Int).Mul(new(big.Int).ModInverse(k, N), new(big.Int).Add(new(big.Int).SetBytes(hash[:]), new(big.Int).Mul(r, priv.D)))
s.Mod(s, N)

asn1Signature, err := asn1.Marshal(EcdsaSignature{R: r, S: s})
```

Una firma de ECDSA son básicamente 2 valores $(r, s)$ que se calculan de la siguiente forma:

$$
\begin{align*}
r &= (k \cdot G)_\mathrm{x} \\
s &= k^{-1} \cdot (H(m) + r \cdot d) \mod{n}
\end{align*}
$$

Donde:

- $G$ es el punto generador de la curva utilizada (en este caso [P256](https://std.neuromancer.sk/nist/P-256))
- $n$ es el orden de $G$ en la curva elíptica
- $H$ es una función _hash_ (en este caso SHA256)
- $d$ es la clave privada de ECDSA
- $k$ es un valor _nonce_ aleatorio
- $m$ es el mensaje a firmar

Aunque ECDSA tenga relación con curvas elípticas, el cálculo de $(r, s)$ es esencialmente aritmética modular. En los retos de firmas digitales, y en concreto de ECDSA, el fallo suele estar en el cálculo del _nonce_ $k$. Se podría hallar la clave privada $d$ en los siguientes casos:

- Si se reutiliza el mismo _nonce_ para dos firmas distintas,
- Si Se utilizan _nonces_ relacionados para varias firmas,
- Si los _nonces_ están sesgados y no cubren el espacio completo $[1, n)$

Si miramos cómo se calcula $k$ en el reto, hace uso de un `reader`:

```go
random := make([]byte, 32)
rand.Read(random)

var results []SignResult
reader := &CustomReader{state: 12345, random: random}
```

Y esta estructura `CustomReader` es la siguiente:

```go
type CustomReader struct {
	state  int16
	random []byte
}
```

Que implementa el método `Read` para poder funcionar con la API de `crypto/rand` en Go:

```go
var a, c int16 = 31337, 1337

func (r *CustomReader) Read(p []byte) (n int, err error) {
	var s []byte

	for i := range p {
		if i%2 == 0 {
			r.state = a*r.state + c
			s = big.NewInt(int64(r.state)).Bytes()
			p[i] = sha256.Sum256(append(s, r.random...))[i]
		} else {
			p[i] = sha256.Sum256(append(r.random, s...))[i]
		}
	}

	return len(p), nil
}
```

Aquí hay varias cosas a tener en cuenta. Lo primero es que se utiliza un generador lineal congruencial (LCG) para el atributo `r.state`. Sea $s_i$ el valor de `r.state` en un cierto instante, se cumple que:

$$
\begin{cases}
s_0 &\gets 12345 \\
s_{i + 1} &= (a \cdot s_i + c) \mod{2^{16}}
\end{cases}
$$

Nótese que el $\mod{2^{16}}$ viene implícito del uso de variables de tipo `int16`. Tal y como está el LCG, es completamente determinístico, ya que conocemos el estado inicial $s_0$.

Sin embargo, la manera de crear aleatoriedad viene de la mano del atributo `r.random` y un hash SHA256. El valor de `r.random` es completamente aleatorio y no predecible ya que viene de `crypto/random`. Por tanto, es imposible conocer el resultado de estas instrucciones sin conocer el valor de `r.random`, aun sabiendo `s`:

```go
p[i] = sha256.Sum256(append(s, r.random...))[i]
// ...
p[i] = sha256.Sum256(append(r.random, s...))[i]
```

El fallo aquí radica en el uso de $\mod{2^{16}}$, porque implica que el LCG tiene un número máximo de estados posibles: exactamente $\mod{2^{16}}$. Por tanto, $s_i = s_{i + 2^{16}}$. Entonces si conseguimos que el LCG sobrepase este límite, podremos encontrar una situación de reutilización del _nonce_.

Para conseguir esto, es necesario calcular $2^{12} + 1$ firmas, ya que por cada firma, el LCG se actualiza $32 / 2 = 16 = 2^4$ veces, por lo que para que el LCG se actualice $2^{16}$ veces, se necesitan $2^{16} / 2^4 = 2^{12}$ firmas. La siguiente firma utilizará el mismo nonce que la primera firma de todas.

Suponiendo dos mensajes distintos $m_1$ y $m_2$, sean $h_1 = H(m_1)$ y $h_2 = H(m_2)$ y sus firmas $(r_1, s_1)$ y $(r_2, s_2)$. Entonces, se tiene un sistema de dos ecuaciones y dos incógnitas en el que se puede despejar fácilmente $d$

$$
\begin{align*}
\left \{
\begin{align*}
s_1 = k^{-1} \cdot (h_1 + r_1 \cdot d) \mod{n} \\
s_2 = k^{-1} \cdot (h_2 + r_2 \cdot d) \mod{n}
\end{align*} \right\} \Longrightarrow \\ \\
 \Longrightarrow d = (h_1 s_2 - h_2 s_1) \cdot (r_2 s_1 - r_1 s_2)^{-1} \mod{n}
\end{align*}
$$

Para obtener la flag se debe firmar la clave pública con la clave privada asociada $d$ (lo que se conoce como prueba de posesión):

```go
valid := ecdsa.Verify(publicKey, hash[:], sig.R, sig.S)

// Proof of Possession
if valid && bytes.Equal(docBytes, pk) {
	return c.JSON(fiber.Map{
		"filename": docFile.Filename,
		"valid":    valid,
		"flag":     os.Getenv("FLAG"),
	})
}
```

Lo único que falta es implementarlo en Python y escribir la lógica de crear las firmas mediante peticiones web y extraer los valores $(r_1, s_1)$ y $(r_2, s_2)$ de las firmas serializadas con ASN.1:

```py
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
```

> **flag: clctf{0tr0_n0nc3_r3us3_3n_3cd5a...}**
