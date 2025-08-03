#!/bin/bash
# Script pour corriger l'erreur CSRF

echo "Correction de l'erreur CSRF..."

# Se connecter au VPS et exécuter les commandes
ssh root@148.230.105.25 << 'EOF'
cd /var/www/globibat

# Arrêter l'application
pkill -f 'python.*run.py'

# Exporter la SECRET_KEY
echo 'export SECRET_KEY="votre-cle-secrete-tres-longue-et-complexe-2025"' >> ~/.bashrc
export SECRET_KEY="votre-cle-secrete-tres-longue-et-complexe-2025"

# Créer/mettre à jour le fichier .env
cat > .env << 'ENVFILE'
# Configuration Flask
FLASK_ENV=production
SECRET_KEY=votre-cle-secrete-tres-longue-et-complexe-2025

# Database MySQL
DATABASE_URL=mysql+pymysql://globibat_user:Miser1597532684$@localhost/globibat_crm

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=info@globibat.com
MAIL_PASSWORD=Miser1597532684$
ENVFILE

# Redémarrer l'application
source venv/bin/activate
nohup python run.py > app.log 2>&1 &

echo "Application redémarrée avec SECRET_KEY!"
sleep 3
ps aux | grep 'python.*run.py' | grep -v grep
EOF