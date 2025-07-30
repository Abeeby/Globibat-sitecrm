#!/usr/bin/env python3
"""
Script pour tester la page index.html localement
"""

import os
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Ajouter les headers CORS pour les fonts
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def start_server(port=8080):
    """Démarre un serveur HTTP local"""
    server = HTTPServer(('localhost', port), MyHTTPRequestHandler)
    print(f"🌐 Serveur démarré sur http://localhost:{port}")
    print("📄 Page principale : http://localhost:{port}/index.html")
    print("🛑 Appuyez sur Ctrl+C pour arrêter le serveur")
    
    # Ouvrir automatiquement dans le navigateur
    time.sleep(1)
    webbrowser.open(f'http://localhost:{port}/index.html')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Serveur arrêté")
        server.shutdown()

if __name__ == "__main__":
    # Vérifier que index.html existe
    if not os.path.exists('index.html'):
        print("❌ Erreur : index.html introuvable!")
        print("Assurez-vous d'être dans le bon répertoire")
        exit(1)
    
    print("=== Test de la page Globibat ===")
    print("✅ index.html trouvé")
    
    # Démarrer le serveur
    start_server()