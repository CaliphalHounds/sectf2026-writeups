from flask import Flask, request, redirect, render_template, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__, template_folder='static')
app.secret_key = "6c7b8a9f0e1d2c3b4a5f6e7d8c9b0aa7f8b92d3c1e4b5a6f8d9e0c1b2a3f4e5d"

DB_PATH = "data/users.db"
BASE_FILES_DIR = os.path.abspath("files")
FILES_DIR = "files"
os.makedirs("data", exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    user_louden = "louden"
    pass_louden = generate_password_hash("M4st4rH4ck3r567!")
    cur.execute("INSERT OR IGNORE INTO users (user, password) VALUES (?, ?)", (user_louden, pass_louden))
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('files_listing'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form.get('user').lower()
        password_input = request.form.get('password')

        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        row = cur.execute("SELECT * FROM users WHERE user = ?", (user_input,)).fetchone()
        db.close()

        if row and check_password_hash(row['password'], password_input):
            session['user'] = row['user']
            return redirect(url_for('files_listing'))
        
        flash("Credenciales inválidas.", "error")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/files/')
@app.route('/files/<path:subpath>')
def files_listing(subpath=""):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    requested_path = os.path.normpath(os.path.join(BASE_FILES_DIR, subpath))
    if not requested_path.startswith(BASE_FILES_DIR):
        return "Acceso denegado", 403

    if not os.path.exists(requested_path):
        return "Directorio no encontrado", 404

    items = []
    for item in os.listdir(requested_path):
        item_path = os.path.join(requested_path, item)
        is_dir = os.path.isdir(item_path)
        items.append({
            "name": item,
            "is_dir": is_dir,
            "rel_path": os.path.join(subpath, item)
        })

    return render_template('files.html', items=items, current_path=subpath)

@app.route('/download/<path:filename>')
def download_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    return send_from_directory(BASE_FILES_DIR, filename)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=18971)