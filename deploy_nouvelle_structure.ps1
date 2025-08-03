# Script de déploiement de la nouvelle structure Globibat
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  GLOBIBAT - Déploiement Nouvelle Structure" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$VPS_IP = "148.230.105.25"
$VPS_USER = "root"

Write-Host "`nCréation du dossier templates/website..." -ForegroundColor Green

# Créer le dossier sur le VPS
ssh "${VPS_USER}@${VPS_IP}" "cd /var/www/globibat && mkdir -p app/templates/website"

Write-Host "`nCopie des fichiers..." -ForegroundColor Green

# Copier les nouveaux fichiers
scp app/views/website.py "${VPS_USER}@${VPS_IP}:/var/www/globibat/app/views/"
scp app/views/badge.py "${VPS_USER}@${VPS_IP}:/var/www/globibat/app/views/"
scp app/templates/website/index.html "${VPS_USER}@${VPS_IP}:/var/www/globibat/app/templates/website/"
scp app/templates/website/intranet.html "${VPS_USER}@${VPS_IP}:/var/www/globibat/app/templates/website/"

Write-Host "`nMise à jour des fichiers Python..." -ForegroundColor Green

# Copier les fichiers modifiés
scp app/views/__init__.py "${VPS_USER}@${VPS_IP}:/var/www/globibat/app/views/"
scp app/__init__.py "${VPS_USER}@${VPS_IP}:/var/www/globibat/app/"
scp app/views/main.py "${VPS_USER}@${VPS_IP}:/var/www/globibat/app/views/"

Write-Host "`nRedémarrage de l'application..." -ForegroundColor Green

ssh "${VPS_USER}@${VPS_IP}" @"
cd /var/www/globibat
pkill -f 'python.*run.py' || true
sleep 2
source venv/bin/activate
nohup python run.py > app.log 2>&1 &
sleep 3
echo 'Application redémarrée!'
ps aux | grep 'python.*run.py' | grep -v grep
"@

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  URLs de la nouvelle structure:" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  SITE PUBLIC:" -ForegroundColor Yellow
Write-Host "  http://${VPS_IP}:5000/" -ForegroundColor White
Write-Host ""
Write-Host "  ACCES INTRANET (caché):" -ForegroundColor Yellow
Write-Host "  http://${VPS_IP}:5000/intranet" -ForegroundColor White
Write-Host ""
Write-Host "  SYSTEMES INTERNES:" -ForegroundColor Yellow
Write-Host "  CRM: http://${VPS_IP}:5000/crm/login" -ForegroundColor White
Write-Host "  Badge: http://${VPS_IP}:5000/employee/badge" -ForegroundColor White
Write-Host ""
Write-Host "  Admin: info@globibat.com / Miser1597532684$" -ForegroundColor Gray
Write-Host "  Badges: 001, 002, 003" -ForegroundColor Gray
Write-Host "================================================" -ForegroundColor Cyan