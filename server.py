import os
import uuid
from flask import Flask, request, render_template_string, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Add secret key for flash messages

UPLOAD_FOLDER = 'logs'
ALLOWED_EXTENSIONS = {'eval'}
DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'linuxbench.equistamp.io')
BASE_URL = f'http://{DOMAIN_NAME}:7575/#/logs/'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_eval_filename_from_url(url):
    """Extract .eval filename from URLs like http://linuxbench.equistamp.io:7575/#/logs/js-6-lose-jobs-atomic.eval"""
    try:
        # Split by / and get the last element
        filename = url.split('/')[-1]
        
        # Check if it's a .eval file
        if filename.endswith('.eval'):
            return filename
            
        return None
    except Exception:
        return None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Upload & Download .eval Files</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
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
            margin-bottom: 10px;
        }
        .section {
            margin-bottom: 40px;
            border-bottom: 1px solid #eee;
            padding-bottom: 30px;
        }
        .section:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }
        h2 {
            color: #555;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        input[type="file"], input[type="url"] {
            padding: 10px;
            border: 2px dashed #ddd;
            border-radius: 4px;
            width: 100%;
            box-sizing: border-box;
        }
        input[type="url"] {
            border-style: solid;
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
        .download-btn {
            background-color: #28a745;
        }
        .download-btn:hover {
            background-color: #218838;
        }
        .error {
            color: #dc3545;
            margin-top: 10px;
            padding: 10px;
            background-color: #f8d7da;
            border-radius: 4px;
        }
        .success {
            color: #155724;
            margin-top: 10px;
            padding: 10px;
            background-color: #d4edda;
            border-radius: 4px;
        }
        .view-link {
            text-align: center;
            margin-bottom: 30px;
        }
        .view-link a {
            color: #007bff;
            text-decoration: none;
            font-weight: bold;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .help-text {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>LinuxBench .eval Files</h1>
        
        <div class="view-link">
            <a href="{{ base_url }}" target="_blank">View Existing Logs →</a>
        </div>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="error">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="section">
            <h2>Download .eval File</h2>
            <form method="post" action="/download">
                <div class="form-group">
                    <label for="eval_url">Paste .eval URL:</label>
                    <input type="url" name="eval_url" id="eval_url" 
                           placeholder="http://linuxbench.equistamp.io:7575/#/logs/filename.eval" required>
                    <div class="help-text">
                        Paste a URL like: http://linuxbench.equistamp.io:7575/#/logs/js-6-lose-jobs-atomic.eval
                    </div>
                </div>
                <button type="submit" class="submit-btn download-btn">Download File</button>
            </form>
        </div>
        
        <div class="section">
            <h2>Upload .eval File</h2>
            <form method="post" action="/" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">Choose .eval file:</label>
                    <input type="file" name="file" id="file" accept=".eval" required>
                </div>
                <button type="submit" class="submit-btn">Upload File</button>
            </form>
            
            <p class="help-text" style="text-align: center; margin-top: 20px;">
                Only .eval files are allowed
            </p>
        </div>
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

@app.route('/download', methods=['POST'])
def download_file():
    eval_url = request.form.get('eval_url', '').strip()
    
    if not eval_url:
        flash('Please provide a valid URL')
        return redirect(url_for('upload_file'))
    
    # Extract filename from URL
    filename = extract_eval_filename_from_url(eval_url)
    
    if not filename:
        flash('Could not extract .eval filename from URL. Please check the URL format.')
        return redirect(url_for('upload_file'))
    
    # Check if file exists in logs directory
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        flash(f'File "{filename}" not found in logs directory')
        return redirect(url_for('upload_file'))
    
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return redirect(url_for('upload_file'))

@app.route('/logs/<filename>')
def serve_log_file(filename):
    """Serve log files directly"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        flash(f'Error serving file: {str(e)}')
        return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80) 