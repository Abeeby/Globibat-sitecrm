# 🏗️ Nouvelle Structure - Globibat

## 📋 Vue d'ensemble

La nouvelle architecture sépare complètement :

### 1. **Site Web Public** (www.globibat.com)
- **URL** : `/`
- **Contenu** : Site vitrine professionnel pour l'entreprise
- **Accès** : Public, optimisé SEO
- **Features** :
  - Page d'accueil moderne avec animations
  - Services de construction
  - Portfolio de projets
  - Formulaire de contact/devis
  - Informations de l'entreprise

### 2. **Système Interne** (Intranet)
- **URL cachée** : `/intranet` ou `/globibat-internal`
- **Contenu** : Portail d'accès aux systèmes internes
- **Accès** : Page de sélection pour CRM ou Badge

#### 2.1 **CRM Globibat**
- **URLs** : 
  - `/crm/login` - Connexion
  - `/crm/dashboard` - Tableau de bord
  - `/crm/clients` - Gestion clients
  - `/crm/projects` - Gestion projets
  - `/crm/quotes` - Devis
  - `/crm/invoices` - Factures
- **Accès** : Administrateurs uniquement
- **Protection** : Login + mot de passe

#### 2.2 **Système de Badge**
- **URL** : `/employee/badge`
- **Accès** : Employés avec numéro de badge
- **Protection** : Badge uniquement

## 🔗 Structure des URLs

```
www.globibat.com/
├── / (Site public)
├── /contact (Formulaire)
├── /mentions-legales
├── /intranet (Page d'accès caché)
│
├── /crm/
│   ├── login
│   ├── dashboard
│   ├── clients/
│   ├── projects/
│   ├── quotes/
│   └── invoices/
│
└── /employee/
    └── badge
```

## 🚀 Accès aux systèmes

### Pour le public :
1. **Site web** : http://148.230.105.25:5000/

### Pour les employés Globibat :
1. **Accès intranet** : http://148.230.105.25:5000/intranet
2. **Badge direct** : http://148.230.105.25:5000/employee/badge

### Pour les administrateurs :
1. **CRM direct** : http://148.230.105.25:5000/crm/login

## 🔒 Sécurité

1. **Site public** : Aucune information sensible
2. **Intranet** : 
   - URL non référencée
   - Peut être protégé par IP
   - Pas de liens depuis le site public
3. **CRM** : Login + mot de passe requis
4. **Badge** : Numéro de badge requis

## 📱 Navigation

### Site Public
- Menu de navigation standard
- Aucun lien vers les systèmes internes
- Focus sur les services et contact

### Intranet
- Page simple avec 2 options :
  1. Accès CRM (pour admin)
  2. Système Badge (pour employés)
- Lien retour vers site public

### CRM
- Menu complet après connexion
- Toutes les fonctionnalités de gestion
- Déconnexion retour à /crm/login

### Badge
- Interface simple
- Pas de navigation (écran unique)
- Retour possible vers intranet

## 🎯 Avantages

1. **Séparation claire** entre public et interne
2. **SEO optimisé** pour le site public uniquement
3. **Sécurité renforcée** par l'isolation
4. **URLs cachées** pour les systèmes internes
5. **Expérience utilisateur** adaptée à chaque public

## 🛠️ Configuration Nginx (pour production)

```nginx
server {
    listen 80;
    server_name www.globibat.com globibat.com;
    
    # Site public
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Systèmes internes (optionnel : restriction IP)
    location ~ ^/(intranet|crm|employee) {
        # allow 192.168.1.0/24;  # Réseau interne
        # deny all;
        
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Résumé

Cette nouvelle structure offre :
- ✅ **Site web public** professionnel et optimisé SEO
- ✅ **Système interne** complètement séparé et caché
- ✅ **Sécurité** renforcée par la séparation
- ✅ **Flexibilité** pour ajouter des restrictions supplémentaires
- ✅ **Expérience utilisateur** optimale pour chaque type d'utilisateur