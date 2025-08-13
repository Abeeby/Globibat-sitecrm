#!/usr/bin/env python3
from flask import Flask, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key-2024'

# Template HTML simple
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Globibat CRM - Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 48px; margin-bottom: 20px; }
        .info { 
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .info p { margin: 10px 0; font-size: 18px; }
        .status { 
            color: #4ade80;
            font-weight: bold;
            font-size: 24px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏗️ Globibat CRM</h1>
        <p class="status">✅ Application en cours d'exécution!</p>
        <div class="info">
            <p>📧 Email: <strong>info@globibat.com</strong></p>
            <p>🔐 Mot de passe: <strong>Miser1597532684$</strong></p>
            <p>🌐 URL: <strong>http://localhost:5000</strong></p>
        </div>
        <p style="margin-top: 30px; opacity: 0.8;">
            L'application principale est en cours de préparation...<br>
            Cette page confirme que Flask fonctionne correctement.
        </p>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/test')
def test():
    return {'status': 'OK', 'message': 'Globibat CRM is running'}

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 GLOBIBAT CRM - MODE TEST")
    print("=" * 60)
    print("📌 URL: http://localhost:5000")
    print("📧 Email: info@globibat.com")
    print("🔐 Mot de passe: Miser1597532684$")
    print("=" * 60)
    print("\n✅ Application démarrée! Ouvrez votre navigateur.")
    print("Appuyez sur Ctrl+C pour arrêter\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)