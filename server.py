import os
import uuid
from flask import Flask, request, render_template_string, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'logs'
ALLOWED_EXTENSIONS = {'eval'}
DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'linuxbench.equistamp.io')
BASE_URL = f'http://{DOMAIN_NAME}:7575/#/logs/'


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Upload .eval File</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .upload-form {
            margin-top: 30px;
        }
        .file-input {
            margin-bottom: 20px;
        }
        input[type="file"] {
            padding: 10px;
            border: 2px dashed #ddd;
            border-radius: 4px;
            width: 100%;
            box-sizing: border-box;
        }
        .submit-btn {
            background-color: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        .submit-btn:hover {
            background-color: #0056b3;
        }
        .error {
            color: #dc3545;
            margin-top: 10px;
        }
        .success {
            color: #28a745;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload .eval File</h1>
        
        <div style="margin-bottom: 20px; text-align: center; border-bottom: 1px solid #eee; padding-bottom: 20px;">
            <a href="{{ base_url }}" target="_blank" style="color: #007bff; text-decoration: none; font-weight: bold;">
                View Existing Logs →
            </a>
        </div>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="error">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form class="upload-form" method="post" enctype="multipart/form-data">
            <div class="file-input">
                <input type="file" name="file" accept=".eval" required>
            </div>
            <button type="submit" class="submit-btn">Upload File</button>
        </form>
        
        <p style="margin-top: 30px; text-align: center; color: #666;">
            Only .eval files are allowed
        </p>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Only .eval files are allowed')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                name, ext = os.path.splitext(filename)
                filename = f"{uuid.uuid4().hex[:8]}-{name}{ext}"
            
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            redirect_url = BASE_URL + filename
            return redirect(redirect_url)
    
    return render_template_string(HTML_TEMPLATE, base_url=BASE_URL)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80) 