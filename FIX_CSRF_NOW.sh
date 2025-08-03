#!/bin/bash
# Script de correction rapide pour l'erreur CSRF

echo "=== CORRECTION RAPIDE DE L'ERREUR CSRF ==="
echo ""

# 1. Se déplacer dans le bon dossier
cd /var/www/globibat

# 2. Arrêter l'application
echo "[1/4] Arrêt de l'application..."
pkill -f 'python.*run.py' 2>/dev/null || true

# 3. Créer le fichier .env avec la configuration
echo "[2/4] Création du fichier .env..."
cat > .env << 'EOF'
# Configuration Flask
SECRET_KEY=globibat-secret-key-2025-production-secure
FLASK_ENV=production

# Database MySQL
DATABASE_URL=mysql+pymysql://globibat_user:Miser1597532684$@localhost/globibat_crm

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=info@globibat.com
MAIL_PASSWORD=Miser1597532684$
EOF

# 4. Exporter la SECRET_KEY
echo "[3/4] Configuration des variables d'environnement..."
export SECRET_KEY="globibat-secret-key-2025-production-secure"
echo 'export SECRET_KEY="globibat-secret-key-2025-production-secure"' >> ~/.bashrc

# 5. Redémarrer l'application
echo "[4/4] Redémarrage de l'application..."
source venv/bin/activate
nohup python run.py > app.log 2>&1 &

# Attendre un peu
sleep 5

# Vérifier que tout fonctionne
echo ""
echo "=== VÉRIFICATION ==="
ps aux | grep 'python.*run.py' | grep -v grep

echo ""
echo "=== TEST DES URLS ==="
echo -n "Site public: "
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/
echo -n "Intranet: "
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/intranet
echo -n "CRM Login: "
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/auth/login
echo -n "Badge: "
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/employee/badge

echo ""
echo "=== TERMINÉ ! ==="
echo ""
echo "Accédez à votre système :"
echo "- Site public: http://148.230.105.25:5000/"
echo "- Intranet: http://148.230.105.25:5000/intranet"
echo "- CRM: http://148.230.105.25:5000/auth/login"
echo "- Badge: http://148.230.105.25:5000/employee/badge"
echo ""
echo "Login CRM: info@globibat.com / Miser1597532684$"