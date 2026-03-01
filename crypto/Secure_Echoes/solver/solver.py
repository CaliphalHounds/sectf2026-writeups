import hashlib
import requests

url = "http://localhost:3000/"
USERNAME = "admin"
PASSWORD = "admin"

def login(username, password):
    r = requests.post(url + "login", data={"username": username, "password": password}, allow_redirects=False)
    if r.status_code == 302:
        return r.cookies.get("connect.sid")
    else:
        raise Exception("Login failed")
    
def send_message(cookie, message):
    r = requests.post(url + "board", data={"note": message}, cookies={"connect.sid": cookie})
    print(f"Sent message: {message} (status code: {r.status_code})")

# def get_last_message():
#     r = requests.get(url + "last")

coeffs = [6, 38, 69, 94, 34, 31, 62, 23, 65, 46, 15, 84, 62, 30, 34, 77, 75, 22, 57, 34, 83, 37, 87, 60, 41, 21, 33, 50, 28, 74, 44, 1, 40, 80, 18, 48, 53, 52, 70, 53]
messages = ['LiqVsOJRgrHFtuWrhGfKVssYPcGVD', '4SI6JI4rdNcfxB72TbrJRWFBFaVyS', 'EnkIGEGDpLNPxpu1XoTbrAf6ENKRG', 'nvHPL7ViBbc2jtTdYvAAKnuIHpqda', 'HD58dN0etyF8RG2JTeMBAjF0yl0At', 'hQHUGfXX8rSJl7k2xceSat8MWewLs', 'xbKmwWc1921UhSvbGKS6CRUiT8Tj6', 'u1jNPXqtrNzfnFA75k6LJoE8oGlXI', 'vNJSDBCSU7S5qXzTuvcv6i6jxDi3n', 'ZHhelyVS4UH9KPqB5ieViWaKpThzL', 'EOdWkzgCoYXIMQgvg0u2MyemqGZMD', 'OjY2TQaIbzShEHPxhb1qClINXEEXv', 'p8QIYBrD0Kqytyapr8w46PgfkSSNE', '0dqVyKi2MS5XK7222OlVd5G4hxxQ1', 'FIIJ47qtjBnF3JV2f3ZjIvgeXzZHk', 'viAI8SkPsSJPTKTtigOBjV2na0l0z', 'sw9PKQvpS9PVOH8ktz5C5hrzBexf3', 'G8rVNTAOxe1Tw7Z79OsdMTbNwRiHC', 'q7PoRK2dAlHewW23tgf0TMyXbAKlB', 'PDg37sTUqNSlxO9oEzBa51EG9qx9O', 'qGvzB5NVmtdL7x3rBf28ZMNCfkSWy', 'mzPgrkxTD343dYB6GG13yuSyyz1G3', 'YOFe1xQTJatX3rO6zaIEjBW48ThYE', 'kRzDWNvfLC7LSrz8JW3sriimgSfeH', 'Xy6gEUP9uVgvyxiFHPIxohca5rIYz', '4Js0eIAVE49TY3wcoVuJqxAZmWnhJ', 'XbptICoG8iYo1ez9cxwhMUax70vQ7', 'FWPsKjYvgItgu5Ws5EPaFzeV0HHpj', 'I4gL331D1O9bsu43yaRgnmjRnQDzG', '5N5w1wf5GrIzYRTfQKsCgpNSfYSP2', 'K2uPxo0eLiaJVe3QSyGTjR9ElnEvN', 'NKTmeWuOMcZOBM3SIbrzeM2aYIXaz', 'cMHfpQ0XWEMGrpT5haZznz0F16wgL', 'Vkf6FmDSPEWgTqRHIAVxCrdyTTt5I', '40X9Zx5Md9RM8USIeRIDPaIdYJTJI', 'L4Xdqz1eMVud3K1QxNINesTPnxwaY', 'QnP5matEiU0PWG4QRgs3kRZ7igIMA', 'T3q5qfUcIbtguqVeTTpYkkJaZKiFp', 'Sd4iRFhrHYFPL1oNqwrofnYmfWwZY', 'zXzRmdsNUbU4lgwIGehTWjw6533xm']

# Sanitty check
total = 0
# totals = []
for c, m in zip(coeffs, messages):
    for _ in range(c):
        total += int(hashlib.sha256(m.encode()).hexdigest(), 16)
        total += pow(int.from_bytes(m.encode(), 'big'), 4, 2**256)
        total += 3*pow(int.from_bytes(m.encode(), 'big'), 3, 2**256)
        total += 3*pow(int.from_bytes(m.encode(), 'big'), 2, 2**256)
        total += 7*int.from_bytes(m.encode(), 'big')
        total %= 2**256
        # totals.append(total)
print(f"Sanity check total: {total} (should be 0)")
assert total == 0, "Sanity check failed: total is not 0 mod 2^256"

cookie = login(USERNAME, PASSWORD)
for c, m in zip(coeffs, messages):
    for _ in range(c):
        send_message(cookie, m)


