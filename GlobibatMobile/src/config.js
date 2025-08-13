export default {
  // Configuration API
  API_URL: 'http://localhost:5001',
  SOCKET_URL: 'http://localhost:5001',
  
  // Pour la production, utilisez votre IP ou domaine
  // API_URL: 'http://192.168.1.100:5001',
  // SOCKET_URL: 'http://192.168.1.100:5001',
  
  // Configuration de l'app
  APP_NAME: 'Globibat CRM',
  COMPANY_NAME: 'Globibat SA',
  
  // Couleurs du thème
  colors: {
    primary: '#005BBB',
    secondary: '#FF7A00',
    success: '#27AE60',
    warning: '#FF7A00',
    danger: '#DC3545',
    info: '#17A2B8',
    light: '#F4F6F8',
    dark: '#2C3E50',
  },
  
  // Timeouts
  REQUEST_TIMEOUT: 30000,
  SOCKET_TIMEOUT: 10000,
  
  // Stockage
  STORAGE_KEYS: {
    TOKEN: '@token',
    USER: '@user',
    SETTINGS: '@settings',
    CACHE: '@cache',
  },
  
  // Pagination
  PAGE_SIZE: 20,
  
  // Types de badges (avec matricule)
  BADGE_TYPES: {
    ENTREE: 'Entrée',
    SORTIE: 'Sortie',
    PAUSE: 'Pause',
    REPRISE: 'Reprise',
  },
  
  // Statuts employés
  EMPLOYEE_STATUS: {
    ACTIF: 'Actif',
    CONGE: 'En congé',
    MALADIE: 'Maladie',
    ABSENT: 'Absent',
    INACTIF: 'Inactif',
  },
  
  // Types de clients
  CLIENT_TYPES: {
    PARTICULIER: 'Particulier',
    ENTREPRISE: 'Entreprise',
    PUBLIC: 'Public',
  },
  
  // Statuts factures
  INVOICE_STATUS: {
    BROUILLON: 'Brouillon',
    ENVOYEE: 'Envoyée',
    PAYEE: 'Payée',
    EN_RETARD: 'En retard',
    ANNULEE: 'Annulée',
  },
};