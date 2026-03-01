from flask import Flask, request, render_template_string, send_from_directory
import os


app = Flask(__name__)


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return "Deshabilitado"

    files = os.listdir(app.config['UPLOAD_FOLDER'])

    return render_template_string('''
        <!doctype html>
        <title>Servidor M32C</title>
        <h2>Recibido:</h2>
        {% for f in files %}
          <div style="margin-bottom:20px;">
            {% if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg') %}
              <img src="{{ url_for('uploaded_file', filename=f) }}" style="max-width:300px;">
            {% elif f.lower().endswith('.3gp') %}
              <audio controls>
                <source src="{{ url_for('uploaded_file', filename=f) }}" type="audio/3gp">
              </audio>
            {% endif %}
            <p>{{ f }}</p>
          </div>
        {% endfor %}
    ''', files=files)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=False)
