# Script PowerShell pour deployer et tester l'application Globibat CRM

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  GLOBIBAT CRM - Deploiement et Test" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Configuration
$VPS_IP = "148.230.105.25"
$VPS_USER = "root"
$LOCAL_PATH = Get-Location
$REMOTE_PATH = "/var/www/globibat"

# 1. Upload des nouveaux fichiers
Write-Host ""
Write-Host "Upload des fichiers de design professionnel..." -ForegroundColor Green

# Copier les fichiers un par un
Write-Host "   Copie de professional-style.css..."
scp "app/static/css/professional-style.css" "${VPS_USER}@${VPS_IP}:${REMOTE_PATH}/app/static/css/"

Write-Host "   Copie de dashboard_pro.html..."
scp "app/templates/dashboard_pro.html" "${VPS_USER}@${VPS_IP}:${REMOTE_PATH}/app/templates/"

Write-Host "   Creation du dossier badge..."
ssh "${VPS_USER}@${VPS_IP}" "mkdir -p ${REMOTE_PATH}/app/templates/badge"

Write-Host "   Copie de index_pro.html..."
scp "app/templates/badge/index_pro.html" "${VPS_USER}@${VPS_IP}:${REMOTE_PATH}/app/templates/badge/"

Write-Host "   Copie de test_and_fix.py..."
scp "test_and_fix.py" "${VPS_USER}@${VPS_IP}:${REMOTE_PATH}/"

# 2. Executer le script de test
Write-Host ""
Write-Host "Execution des tests et corrections..." -ForegroundColor Green
ssh "${VPS_USER}@${VPS_IP}" "cd ${REMOTE_PATH} && source venv/bin/activate && python test_and_fix.py"

# 3. Redemarrer l'application
Write-Host ""
Write-Host "Redemarrage de l'application..." -ForegroundColor Green
ssh "${VPS_USER}@${VPS_IP}" "cd ${REMOTE_PATH} && pkill -f 'python.*run.py' || true"
Start-Sleep -Seconds 2
ssh "${VPS_USER}@${VPS_IP}" "cd ${REMOTE_PATH} && source venv/bin/activate && nohup python run.py > app.log 2>&1 &"
Start-Sleep -Seconds 3

# 4. Verifier le statut
Write-Host ""
Write-Host "Verification du statut..." -ForegroundColor Green
ssh "${VPS_USER}@${VPS_IP}" "ps aux | grep 'python.*run.py' | grep -v grep"

# 5. Afficher les URLs
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  URLs de test disponibles:" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Page d'accueil: http://${VPS_IP}:5000/" -ForegroundColor White
Write-Host "  Connexion: http://${VPS_IP}:5000/auth/login" -ForegroundColor White
Write-Host "  Dashboard: http://${VPS_IP}:5000/dashboard" -ForegroundColor White
Write-Host "  Badge: http://${VPS_IP}:5000/badge" -ForegroundColor White
Write-Host ""
Write-Host "  Identifiants admin:" -ForegroundColor Yellow
Write-Host "  Email: info@globibat.com" -ForegroundColor White
Write-Host "  Mot de passe: Miser1597532684$" -ForegroundColor White
Write-Host ""
Write-Host "  Badges test: 001, 002, 003" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Deploiement termine!" -ForegroundColor Green