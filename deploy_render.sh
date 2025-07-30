#!/bin/bash

echo "🚀 Préparation du déploiement sur Render.com"
echo "==========================================="

# Vérifier si Git est installé
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé. Installez Git d'abord."
    exit 1
fi

# Initialiser Git si nécessaire
if [ ! -d ".git" ]; then
    echo "📦 Initialisation de Git..."
    git init
    git add .
    git commit -m "Initial commit - Système de badgeage Globibat"
fi

# Instructions pour l'utilisateur
echo ""
echo "✅ Votre application est prête pour le déploiement !"
echo ""
echo "📋 Étapes suivantes :"
echo ""
echo "1. Créez un compte GitHub si vous n'en avez pas : https://github.com"
echo ""
echo "2. Créez un nouveau repository sur GitHub"
echo ""
echo "3. Connectez votre code à GitHub :"
echo "   git remote add origin https://github.com/VOTRE_USERNAME/globibat-badge.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. Créez un compte sur Render.com : https://render.com"
echo ""
echo "5. Sur Render :"
echo "   - Cliquez sur 'New +' → 'Web Service'"
echo "   - Connectez votre GitHub"
echo "   - Sélectionnez votre repository 'globibat-badge'"
echo "   - Render détectera automatiquement la configuration"
echo ""
echo "6. Votre application sera accessible à :"
echo "   https://globibat-badge.onrender.com"
echo ""
echo "💡 Conseil : Le premier déploiement peut prendre 5-10 minutes"
echo ""
echo "📚 Documentation complète : voir GUIDE_DEPLOIEMENT.md" 