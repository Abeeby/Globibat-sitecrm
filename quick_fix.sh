#!/bin/bash
# Script rapide pour corriger le template manquant

echo "================================================"
echo "  GLOBIBAT CRM - Correction Rapide"
echo "================================================"

# Connexion SSH et correction
ssh root@148.230.105.25 << 'ENDSSH'
cd /var/www/globibat

# Créer le template index.html
cat > app/templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Globibat SA - Construction Suisse Romande</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="bi bi-building"></i> GLOBIBAT</a>
            <a class="btn btn-warning" href="/auth/login">Connexion CRM</a>
        </div>
    </nav>
    <div class="container text-center py-5">
        <h1>Bienvenue chez Globibat SA</h1>
        <p class="lead">Entreprise de construction en Suisse romande</p>
        <div class="mt-4">
            <a href="/auth/login" class="btn btn-primary btn-lg">Accès CRM</a>
            <a href="/badge" class="btn btn-secondary btn-lg">Interface Badge</a>
        </div>
    </div>
</body>
</html>
EOF

# Mettre à jour les vues pour utiliser les templates pro
sed -i "s/dashboard.html/dashboard_pro.html/g" app/views/main.py
sed -i "s|badge/index.html|badge/index_pro.html|g" app/views/badge.py

# Relancer l'application
pkill -f "python.*run.py" || true
source venv/bin/activate
nohup python run.py > app.log 2>&1 &

echo "Application redémarrée!"
sleep 3
ps aux | grep "python.*run.py" | grep -v grep
ENDSSH

echo ""
echo "================================================"
echo "  Correction appliquée!"
echo "================================================"
echo "  Testez sur: http://148.230.105.25:5000/"
echo "================================================"