#!/bin/bash

# Script de lancement du CRM Globibat - Design Moderne
# =====================================================

echo "╔══════════════════════════════════════════════════════╗"
echo "║        🚀 CRM GLOBIBAT - DESIGN MODERNE 🚀          ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "🔧 Vérification de l'environnement..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi
echo "✅ Python 3 détecté"

# Créer l'environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Installer/Mettre à jour les dépendances
echo "📚 Installation des dépendances..."
pip install -q --upgrade pip
pip install -q flask flask-sqlalchemy flask-login

# Exporter les variables d'environnement
export FLASK_APP=app_modern.py
export FLASK_ENV=development
export SECRET_KEY="dev-secret-key-globibat-2024"

# Effacer l'écran et afficher les informations
clear
echo "╔══════════════════════════════════════════════════════╗"
echo "║        🎨 CRM GLOBIBAT - INTERFACE MODERNE 🎨        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "📌 INFORMATIONS DE CONNEXION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 URL d'accès : http://localhost:5000"
echo ""
echo "📍 PAGES PRINCIPALES :"
echo "   • Dashboard    : http://localhost:5000/modern/dashboard"
echo "   • Chantiers    : http://localhost:5000/modern/chantiers"
echo "   • Factures     : http://localhost:5000/modern/factures"
echo "   • Employés     : http://localhost:5000/modern/employes"
echo ""
echo "🎯 FONCTIONNALITÉS CLÉS :"
echo "   • Mode clair/sombre (switch dans le header)"
echo "   • Planning Gantt interactif"
echo "   • Carte des chantiers"
echo "   • Timeline avec photos"
echo "   • Chat par chantier"
echo "   • Suivi budgétaire en temps réel"
echo ""
echo "⌨️  RACCOURCIS :"
echo "   • Ctrl+C : Arrêter le serveur"
echo "   • F5     : Rafraîchir la page"
echo "   • F12    : Ouvrir les outils développeur"
echo ""
echo "═══════════════════════════════════════════════════════"
echo "🚀 Démarrage du serveur..."
echo "═══════════════════════════════════════════════════════"
echo ""

# Lancer l'application
python3 app_modern.py