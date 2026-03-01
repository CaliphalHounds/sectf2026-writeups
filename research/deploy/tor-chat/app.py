from flask import Flask, request, redirect, render_template, url_for, session
import os

app = Flask(__name__, template_folder='static')
app.secret_key = "6c7b8a9f0e1d2c3b4a5f6e7d8c9b0aa7f8b92d3c1e4b5a6f8d9e0c1b2a3f4e5d"

ACCESS_CODE = "LOU-HOSP-8821"

@app.route('/')
def index():
    if session.get('authorized'):
        return redirect(url_for('chat'))
    return render_template('login.html', error=request.args.get('error'))

@app.route('/auth', methods=['POST'])
def auth():
    code_input = request.form.get('code', '').strip()
    if code_input == ACCESS_CODE:
        session['authorized'] = True
        return redirect(url_for('chat'))
    return redirect(url_for('index', error="CÓDIGO INVÁLIDO"))

@app.route('/chat')
def chat():
    if not session.get('authorized'):
        return redirect(url_for('index'))
    return render_template('chat.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8821)