# Script PowerShell pour déployer et tester l'application Globibat CRM
# Usage: .\deploy_and_test.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  GLOBIBAT CRM - Déploiement et Test" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Configuration
$VPS_IP = "148.230.105.25"
$VPS_USER = "root"
$LOCAL_PATH = Get-Location
$REMOTE_PATH = "/var/www/globibat"

# Fonction pour exécuter des commandes SSH
function Execute-SSH {
    param($Command)
    Write-Host "`n🔧 Exécution: $Command" -ForegroundColor Yellow
    ssh "$VPS_USER@$VPS_IP" $Command
}

# 1. Upload des nouveaux fichiers
Write-Host "`n📤 Upload des fichiers de design professionnel..." -ForegroundColor Green

# Créer une liste des fichiers à copier
$filesToCopy = @(
    "app/static/css/professional-style.css",
    "app/templates/dashboard_pro.html",
    "app/templates/badge/index_pro.html",
    "test_and_fix.py"
)

foreach ($file in $filesToCopy) {
    Write-Host "   Copie de $file..."
    scp "$LOCAL_PATH/Globibat_Badge_System/$file" "${VPS_USER}@${VPS_IP}:${REMOTE_PATH}/$file"
}

# 2. Exécuter le script de test et correction
Write-Host "`n🔍 Exécution des tests et corrections..." -ForegroundColor Green
$testCommand = @"
cd $REMOTE_PATH && \
source venv/bin/activate && \
python test_and_fix.py
"@
Execute-SSH $testCommand

# 3. Redémarrer l'application
Write-Host "`n🔄 Redémarrage de l'application..." -ForegroundColor Green
$restartCommand = @"
cd $REMOTE_PATH && \
pkill -f 'python.*run.py' || true && \
sleep 2 && \
source venv/bin/activate && \
nohup python run.py > app.log 2>&1 & && \
sleep 3 && \
echo 'Application redémarrée'
"@
Execute-SSH $restartCommand

# 4. Vérifier le statut
Write-Host "`n✅ Vérification du statut..." -ForegroundColor Green
$statusCommand = @"
ps aux | grep 'python.*run.py' | grep -v grep && \
curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost:5000/
"@
Execute-SSH $statusCommand

# 5. Afficher les URLs de test
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  URLs de test disponibles:" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  🌐 Page d'accueil: http://$VPS_IP`:5000/" -ForegroundColor White
Write-Host "  🔐 Connexion: http://$VPS_IP`:5000/auth/login" -ForegroundColor White
Write-Host "  📊 Dashboard: http://$VPS_IP`:5000/dashboard" -ForegroundColor White
Write-Host "  🎫 Badge: http://$VPS_IP`:5000/badge" -ForegroundColor White
Write-Host "`n  Identifiants admin:" -ForegroundColor Yellow
Write-Host "  Email: info@globibat.com" -ForegroundColor White
Write-Host "  Mot de passe: Miser1597532684$" -ForegroundColor White
Write-Host "`n  Badges test: 001, 002, 003" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan

# 6. Option pour ouvrir le navigateur
$response = Read-Host "`nVoulez-vous ouvrir l'application dans votre navigateur? (O/N)"
if ($response -eq 'O' -or $response -eq 'o') {
    Start-Process "http://$VPS_IP`:5000/"
}

Write-Host "`n✅ Déploiement terminé!" -ForegroundColor Green