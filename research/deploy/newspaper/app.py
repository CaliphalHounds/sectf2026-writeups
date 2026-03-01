from flask import Flask, request, redirect, render_template, url_for, session
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "6c7b8a9f0e1d2c3b4a5f6e7d8c9b0aa7f8b92d3c1e4b5a6f8d9e0c1b2a3f4e5d"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/noticia/<int:id>')
def noticia(id):
    return render_template(f'noticia{id}.html')

@app.route('/exclusiva/feudal-cats')
def noticia_louden():
    return render_template('noticia-feudal-cats.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7371)