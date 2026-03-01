# Secure Echoes

> CTF Track Securiters - RootedCON 2026

> 27/02/2026 18:00 CEST - 01/03/2026 18:00 CEST

* Categoría: Criptografía
* Autor: manbolq
* Dificultad: ★★★
* Etiquetas: LLL

## Descripción
    
    ¿Tienes secretos que guardar? No te preocupes, aquí están seguros.

## Resolución

Se presenta una aplicación web en la que el usuario, una vez registrado, puede escribir sus secretos. Estos secretos se cifran utilizando AES en modo CTR, cambiando la clave de cifrado entre mensajes. El objetivo es encontrar un conjunto de mensajes que haga que se reutilice la clave usada para cifrar la flag. Una vez logrado, se descifra la flag.


### Estructura de la base de datos

La base de datos usada para la aplicación es lo más sencilla posible:

```sql
CREATE TABLE users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE,
  password TEXT,
  key BLOB
);

CREATE TABLE notes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  ciphertext BLOB
);
```

La tabla `users` almacena el nombre de usuario y la contraseña del usuario, junto a la clave con la que se cifrará su siguiente mensaje. La tabla `notes` almacena el identificador del usuario que almacenó la nota y la nota cifrada.


### Análisis de la aplicación web

Una parte interesante de la aplicación web es el registro de usuario. Esta es la parte del archivo `app.js` que gestiona el registro de usuarios:

```js
app.post("/register", (req, res) => {
  const {u,p} = req.body
  const key = crypto.randomBytes(32)
  console.log(`Registering user: ${u} with key: ${bufToBig(key)}`)

  try {
    const info = db.prepare(
      "INSERT INTO users(username,password,key) VALUES(?,?,?)"
    ).run(u,p,key)

    const uid = info.lastInsertRowid
    const cipher = new CipherState(bufToBig(key))
    const ct = cipher.encrypt(FLAG)

    db.prepare(
      "INSERT INTO notes(user_id,ciphertext) VALUES(?,?)"
    ).run(uid,ct)

    updateKey(uid,cipher)
  } catch {
    return res.send("user exists")
  }
  res.redirect("/login")
})
```

Se genera una clave aleatoria de 32 bytes que se almacena en la tabla `users`, junto al nombre de usuario y contraseña. Se crea un objeto de la clase `CipherState` y se cifra la flag usando la clave. La flag cifrada se añade al conjunto de notas cifradas por el usuario. La clave usada para cifrar la flag en ningún momento se puede conocer.

La otra funcionalidad interesante es la de crear nuevas notas:

```js
app.post("/board", (req, res) => {
  if(!req.session.uid) return res.redirect("/login")

  const noteText = req.body.note ? req.body.note.trim() : "";

  if (noteText.length === 0) {
    return res.redirect("/board");
  }

  const note = Buffer.from(noteText)
  const cipher = getCipher(req.session.uid)
  
  cipher.reseed(note)
  const ct = cipher.encrypt(note)

  db.prepare(
    "INSERT INTO notes(user_id,ciphertext) VALUES(?,?)"
  ).run(req.session.uid, ct)

  updateKey(req.session.uid, cipher)
  
  res.redirect("/board")
})
```

Cuando el usuario envía una nota, el servidor extrae la clave del usuario y genera un objeto de la clase `CipherState`, con esa clave.

```js
function getCipher(uid) {
  const row = db.prepare("SELECT key FROM users WHERE id=?").get(uid)
  return new CipherState(bufToBig(row.key))
}
```

Después, ejecuta el método `reseed` involucrando la propia nota del usuario y cifra la nota con la nueva clave obtenida tras el `reseed`. Finalmente añade esa nota cifrada a la base de datos.

### Análisis del cifrado

Veamos el archivo `cipher.js`, que contiene la clase `CipherState`. Primero, encontramos dos funciones auxiliares que permiten pasar de número a entero a una cadena de bytes:

```js
function bufToBig(b) {
  if (b.length === 0) return 0n;
  return BigInt("0x" + b.toString("hex"))
}

function bigToBuf(x) {
  return Buffer.from(x.toString(16).padStart(64,"0"), "hex")
}
```

En la definición de la clase `CipherState`, el único atributo es `key`:

```js
constructor(key) {
    this.key = key
}
```

Viendo el método `encrypt`, vemos que el cifrado es AES-256 en modo CTR, usando la clave del objeto:

```js
encrypt(pt) {
    const cipher = crypto.createCipheriv(
      "aes-256-ctr",
      bigToBuf(this.key),
      IV
    )
    return Buffer.concat([cipher.update(pt), cipher.final()])
}
```

Es importante notar que el `IV` utilizado es constante y no cambia. Está definido anteriormente como:

```js
const IV = Buffer.alloc(16,0)
```

Es decir, el IV se reutiliza. Esto significa que si se usa la misma clave dos veces y conocemos uno de los textos planos, podremos recuperar el otro. Así, para recuperar la flag, debemos provocar una colisión en las claves usadas. Para ello, analicemos el método `reseed` (el más importante):

```js
reseed(msg) {
    const h = bufToBig(crypto.createHash("sha256").update(msg).digest()) % MOD

    const m = bufToBig(msg) % MOD
    const m2 = (m * m) % MOD
    const m3 = (m2 * m) % MOD
    const m4 = (m3 * m) % MOD
    const extra = (m4 + 3n*m3 + 3n*m2 + 7n*m) % MOD

    this.key = (this.key + h + extra) % MOD
    console.log(`Reseeded with message: ${msg.toString()} (h: ${h}, m: ${m}, extra: ${extra})`)
    console.log(`New key: ${this.key}`)
}
```

Este método actualizado el valor del atributo `key`. A partir de un mensaje `msg`, la nueva clave es actualizada de la siguiente forma (simplificando la notación):

```
key = SHA256(m) + m^4 + 3*m^3 + 3*m^2 + 7*m   (mod 2^256)
```

El objetivo es encontrar un conjunto de mensajes $m_1, m_2, ...., m_n$, que satisfaga la siguiente condición:

$$\sum_{i=1}^n \text{SHA256}(m_i) + m_i^4 + 3m_i^3 + 3m_i^2 + 7m_i \equiv 0 \quad (\text{mod} \ 2^{256})$$

Entonces, se enviarían estos mensajes y, el último de ellos, se cifraría usando la misma clave que la flag, permitiéndonos recuperar la flag al reusar el IV. Al introducir el hash SHA256, esta actualización de clave deja de ser polinómica, lo que hace mucho más difícil encontrar mensajes que puedan hacer que la clave se reutilice.

### Encontrando los mensajes

Para encontrar los mensajes, podemos usar la siguiente técnica: encontrar un conjunto de coeficientes $c_i$ (cuántas veces enviamos cada mensaje) tales que la suma de los desplazamientos de clave sea múltiplo de $2^{256}$. Si definimos $\Delta K_i$ como el cambio en la clave tras procesar el mensaje $m_i$, buscamos:

$$\sum_{i=1}^n c_i \Delta K_i \equiv 0 \ (\text{mod} \ 2^{256})$$

Este es un problema de suma modular que puede resolverse mediante reducción de retículos. Construimos una matriz donde buscaremos un vector corto que contenga nuestros coeficientes $c_i$. Para asegurar que los coeficientes sean positivos y pequeños (para no enviar miles de peticiones), utilizamos una técnica de embedding (fijando un objetivo en el centro del rango deseado, por ejemplo, 50).

Para hacer esto, podemos usar este script escrito en sagemath:

```py
import hashlib, string, random

flag_length = 48

def generate_hashes(n):
    messages, hashes = [], []
    for _ in range(n):
        # Generamos mensajes aleatorios
        msg = ''.join(random.choices(string.ascii_letters + string.digits, k=48))
        h_int = int(hashlib.sha256(msg.encode()).hexdigest(), 16)
        messages.append(msg); hashes.append(h_int)
    return messages, hashes

def solve_range_sum(messages, hashes, mod_val, max_coeff=100):
    n = len(hashes)
    messages_int = [int.from_bytes(m.encode(), 'big') for m in messages]
    # Calculamos el delta de clave total por cada mensaje
    H = [(h + pow(m, 4, mod_val) + 3*pow(m, 3, mod_val) + 3*pow(m, 2, mod_val) + 7*m) % mod_val for m,h in zip(messages_int, hashes)]
    
    mid = max_coeff / 2
    K1 = 2**600 # Penalización para la suma modular
    K2 = 1
    
    rows = []
    for i in range(n):
        row = [0] * (n + 1)
        row[0] = int(H[i] * K1)
        row[i+1] = K2
        rows.append(row)
        
    rows.append([int(mod_val * K1)] + [0] * n)
    target_row = [0] + [int(-mid * K2)] * n
    
    M = Matrix(ZZ, rows)
    M = M.stack(vector(ZZ, target_row))
    M = M.augment(vector(ZZ, [0]*(n+1) + [1]))

    L = M.LLL()
    
    for row in L:
        if row[0] == 0 and abs(row[-1]) == 1:
            flip = row[-1] 
            coeffs = []
            valid = True
            for i in range(1, n + 1):
                l_i = (row[i] * flip / K2) + mid
                if l_i.is_integer() and 0 <= l_i <= max_coeff:
                    coeffs.append(int(l_i))
                else:
                    valid = False; break
            if valid and any(c > 0 for c in coeffs):
                return coeffs
    return None

MOD = 2**256
N = 40
messages, hashes = generate_hashes(N)
coeffs = solve_range_sum(messages, hashes, MOD)

if coeffs:
    print(f"Coeficientes encontrados: {coeffs}")
    print(f"Mensajes: {messages}")
```

Al ejecutar este script, obtenemos un output parecido a este (puede que con un conjunto de mensajes concreto no obtengamos un resultado que nos sirva, pero podemos ejecutarlo varias vecs hasta que funcione):

```
Coeficientes encontrados: [85, 36, 52, 49, 43, 16, 45, 66, 80, 12, 25, 46, 28, 87, 71, 26, 39, 70, 61, 39, 56, 31, 80, 56, 30, 28, 65, 32, 30, 30, 43, 69, 28, 58, 24, 61, 43, 46, 63, 71]
Mensajes: ['HsMhNFM4JpDOfTQMAU8oivyLRAWq6CaiRa5MAeJIbfurIxcz', '9l8MvvGzKWJ8SIdxIeqmsmb1XITRJKg5C0AMASL0j3UOEmoc', 'Vi81ZfhdmRywc6bg1d6OgulFgDzJm5zMs263pybyciUDV8eM', ...SNIP...]
```

Una vez tenemos el conjunto de mensajes, solo tenemos que interactuar con la aplicación web, hasta haberlos mandado todos. Podemos automatizar esto con este script:

```py
import hashlib
import requests

url = "http://localhost:3000/"
USERNAME = "admin"
PASSWORD = "admin"
coeffs = [] # LA LISTA DE COEFICIENTES
messages = [] # LA LISTA DE MENSAJES

def login(username, password):
    r = requests.post(url + "login", data={"username": username, "password": password}, allow_redirects=False)
    if r.status_code == 302:
        return r.cookies.get("connect.sid")
    else:
        raise Exception("Login failed")
    
def send_message(cookie, message):
    r = requests.post(url + "board", data={"note": message}, cookies={"connect.sid": cookie})
    print(f"Sent message: {message} (status code: {r.status_code})")

# Sanitty check
total = 0
for c, m in zip(coeffs, messages):
    for _ in range(c):
        total += int(hashlib.sha256(m.encode()).hexdigest(), 16)
        total += pow(int.from_bytes(m.encode(), 'big'), 4, 2**256)
        total += 3*pow(int.from_bytes(m.encode(), 'big'), 3, 2**256)
        total += 3*pow(int.from_bytes(m.encode(), 'big'), 2, 2**256)
        total += 7*int.from_bytes(m.encode(), 'big')
        total %= 2**256

print(f"Sanity check total: {total}")
assert total == 0, "Sanity check failed: total is not 0 mod 2^256"

cookie = login(USERNAME, PASSWORD)
for c, m in zip(coeffs, messages):
    for _ in range(c):
        send_message(cookie, m)
```

Finalmente, obtenemos el primer mensaje cifrado (la flag), el último mensaje cifrado y su mensaje en plano correspondiente y ejecutamos las siguientes lineas de python:

```py
from pwn import xor

enc_flag = bytes.fromhex("") # flag cifrada
enc_last_msg = bytes.fromhex("") # ultimo msg cifrado
last_msg = b"" # ultimo mensaje

keystream = xor(last_msg, enc_last_msg)
flag = xor(keystream, enc_flag)
print(f"{flag = }")
```


> **flag: clctf{w0w_m4yb3_y0ur_ech03s_4r3_n0t_th47_s3cur3}**