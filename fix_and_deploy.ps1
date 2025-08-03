# Script de déploiement et correction finale
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  GLOBIBAT CRM - Correction et Déploiement Final" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$VPS_IP = "148.230.105.25"
$VPS_USER = "root"

Write-Host "`nInstructions:" -ForegroundColor Yellow
Write-Host "1. Copiez et exécutez ces commandes sur le VPS" -ForegroundColor White
Write-Host "2. Connectez-vous d'abord: ssh root@$VPS_IP" -ForegroundColor White
Write-Host ""

# Commandes à exécuter sur le VPS
$commands = @"
# 1. Copier le template index.html
cd /var/www/globibat
cat > app/templates/index.html << 'EOF'
$(Get-Content -Path "app/templates/index.html" -Raw)
EOF

# 2. Mettre à jour main.py pour utiliser le bon template
sed -i "s/return render_template('dashboard.html'/return render_template('dashboard_pro.html'/g" app/views/main.py
sed -i "s/return render_template('badge\/index.html'/return render_template('badge\/index_pro.html'/g" app/views/badge.py

# 3. Arrêter l'ancienne instance
pkill -f "python.*run.py" || true

# 4. Relancer l'application
source venv/bin/activate
nohup python run.py > app.log 2>&1 &

# 5. Vérifier le statut
sleep 3
echo "Status de l'application:"
ps aux | grep "python.*run.py" | grep -v grep
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5000/
"@

# Sauvegarder les commandes dans un fichier
$commands | Out-File -FilePath "deploy_commands.txt" -Encoding UTF8

Write-Host "`n📋 Les commandes ont été sauvegardées dans deploy_commands.txt" -ForegroundColor Green
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  URLs de test après déploiement:" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  🌐 Page d'accueil: http://$VPS_IP`:5000/" -ForegroundColor White
Write-Host "  🔐 Connexion: http://$VPS_IP`:5000/auth/login" -ForegroundColor White
Write-Host "  📊 Dashboard: http://$VPS_IP`:5000/dashboard" -ForegroundColor White
Write-Host "  🎫 Badge: http://$VPS_IP`:5000/badge" -ForegroundColor White
Write-Host ""
Write-Host "  Identifiants:" -ForegroundColor Yellow
Write-Host "  Email: info@globibat.com" -ForegroundColor White
Write-Host "  Mot de passe: Miser1597532684`$" -ForegroundColor White
Write-Host ""
Write-Host "  Badges: 001, 002, 003" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan

# Ouvrir le fichier de commandes
notepad deploy_commands.txt