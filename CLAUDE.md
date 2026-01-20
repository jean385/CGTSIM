# Projet CGTSIM - Portail de financement

## 🎯 Mission
Système de gestion de trésorerie pour le Centre de gestion de la trésorerie scolaire intégrée du ministère (CGTSIM).
Gère le financement de 5 centres de services scolaires (CSS) à Montréal via un système d'avances et de billets du marché monétaire.

## 💼 Contexte métier

### Rôle du CGTSIM
- Intermédiaire financier entre les CSS et le marché monétaire
- Reçoit les demandes de financement des CSS
- Emprunte sur le marché monétaire via des billets à court terme
- Verse les avances aux CSS
- Facture les intérêts basés sur le coût des billets + marge

### Flux financier
```
1. CSS soumettent des demandes de fonds (montant + date requise + type)
2. Admin CGTSIM révise toutes les demandes de la semaine
3. Planification : calcul du montant total à emprunter
4. Émission de billets sur le marché monétaire (ex: 1M$ à 4.25% pour 30 jours)
5. CGTSIM verse les avances aux CSS
6. Calcul du taux moyen pondéré des billets
7. Application du taux aux CSS (taux moyen + marge)
8. Facturation des intérêts aux CSS
9. Remboursement via subventions du ministère
```

### Types de financement
- **Avances de fonctionnement** : Besoins opérationnels courants
- **Avances de taxe** : Anticipation des revenus de taxe scolaire
- **Avances de projet** : Financement de projets spécifiques
- **Paiement accéléré de subventions** : Accélération du versement de subventions gouvernementales

## 🏗️ Architecture technique

### Backend
- **Framework** : Django 5.0+
- **API** : Django REST Framework
- **Authentification** : JWT (djangorestframework-simplejwt)
- **Base de données** : 
  - Développement : SQLite
  - Production : PostgreSQL
- **Serveur** : Gunicorn (production)

### Frontend
- **Framework** : React 18+
- **Style** : Tailwind CSS
- **Gestion d'état** : React Hooks (useState, useEffect, useContext)
- **Routing** : React Router
- **API Client** : Axios
- **Build** : Create React App

### Structure du projet
```
cgtsim/
├── backend/
│   ├── cgtsim/          # App principale
│   │   ├── models.py    # Modèles de données
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   └── services.py  # Logique métier
│   ├── config/          # Configuration Django
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── Login.jsx
│   │   ├── PortailCSS.jsx
│   │   ├── PortailAdmin.jsx
│   │   └── apiService.js
│   └── package.json
└── requirements.txt
```

## 📊 Modèles de données principaux

### User
- Authentification personnalisée avec rôles (admin_cgtsim, user_css, viewer)
- Lié à un CSS spécifique pour les utilisateurs CSS
- Support 2FA optionnel

### CSS (Centre de Services Scolaires)
- Code unique (ex: CSS001)
- Informations de contact
- Statut actif/inactif

### DemandeFonds
- Type de demande (fonctionnement, taxe, projet, paiement_accelere)
- Montant demandé
- Date requise
- Statut (pending, approved, rejected, funded)
- Liaison avec CSS et utilisateur créateur
- Historique des changements de statut

### BilletMarcheMonetaire
- Numéro de billet unique
- Montant emprunté
- Taux d'intérêt
- Date d'émission et d'échéance
- Durée en jours
- Statut (active, matured, rolled_over)
- Calcul automatique des intérêts

### Avance
- Lien vers DemandeFonds et BilletMarcheMonetaire
- Montant versé
- Date de versement
- Taux appliqué (taux moyen pondéré des billets)
- Calcul des intérêts dus
- Remboursements liés

### Remboursement
- Lien vers Avance
- Montant remboursé
- Date de remboursement
- Type (subvention, autre)
- Calcul automatique du solde restant

## 🔐 Sécurité et permissions

### Authentification
- JWT tokens (access + refresh)
- Expiration configurable
- Refresh token rotation

### Permissions par rôle

**Administrateur CGTSIM** :
- Voir toutes les demandes de tous les CSS
- Approuver/rejeter les demandes
- Gérer les billets du marché monétaire
- Enregistrer les avances et remboursements
- Voir tous les rapports financiers

**Utilisateur CSS** :
- Voir uniquement les demandes de son CSS
- Créer de nouvelles demandes
- Voir l'historique de ses demandes
- Consulter ses avances et remboursements

**Observateur** :
- Lecture seule sur les données de son CSS

## 💡 Fonctionnalités clés

### Portail CSS
1. **Tableau de bord** : Vue d'ensemble des demandes actives
2. **Nouvelle demande** : Formulaire de soumission
3. **Suivi** : Statut en temps réel des demandes
4. **Historique** : Consultation des demandes passées

### Portail Admin CGTSIM
1. **Demandes en attente** : Liste filtrée et triable
2. **Planification hebdomadaire** : Vue des besoins de la semaine
3. **Gestion des billets** : Enregistrement et suivi
4. **Calcul automatique** : Taux moyen pondéré
5. **Facturation** : Génération automatique des intérêts
6. **Rapports** : Tableaux de bord financiers

### Calculs automatiques

**Taux moyen pondéré** :
```python
taux_moyen = sum(billet.montant * billet.taux for billet in billets) / sum(billet.montant for billet in billets)
```

**Intérêts sur avance** :
```python
interets = montant_avance * taux_applique * (jours / 365)
```

## 🎨 Standards de code

### Python/Django
- **Style** : PEP 8
- **Docstrings** : Google style, en français
- **Type hints** : Utiliser partout où pertinent
- **Validation** : Validators Django + logique custom dans services.py
- **Tests** : pytest-django

### JavaScript/React
- **Style** : Airbnb JavaScript Style Guide
- **Composants** : Functional components avec hooks
- **Nommage** : PascalCase pour composants, camelCase pour fonctions
- **Props** : Toujours avec PropTypes ou TypeScript
- **État** : Hooks (useState, useEffect, useContext)

### Base de données
- **Migrations** : Toujours générer et commiter
- **Nommage** : snake_case pour tables et colonnes
- **Index** : Sur les foreign keys et champs de recherche fréquents
- **Contraintes** : Définir au niveau DB quand possible

## 🚀 Déploiement

### Développement
```bash
# Backend
python manage.py runserver

# Frontend
npm start
```

### Production
- **Backend** : Gunicorn + Nginx
- **Frontend** : Build statique servi par Nginx
- **Base de données** : PostgreSQL
- **Variables d'env** : .env files (jamais commités)

## 📝 Documentation

### API REST
- Endpoints documentés avec DRF browsable API
- Schéma OpenAPI disponible
- Exemples de requêtes/réponses

### Code
- Docstrings en français pour toutes les fonctions publiques
- Comments en français pour logique complexe
- README.md à jour dans chaque dossier important

## 🔄 Workflow Git

### Branches
- `main` : Code en production
- `develop` : Développement actif
- `feature/*` : Nouvelles fonctionnalités
- `fix/*` : Corrections de bugs

### Commits
- Messages en français
- Format : "Type: Description courte"
- Types : feat, fix, docs, refactor, test, chore

### Pull Requests
- Template avec checklist
- Révision de code requise
- Tests passent avant merge

## 🎯 Prochaines étapes / TODO

### Priorité haute
- [ ] Finaliser l'intégration API BNC pour transactions bancaires
- [ ] Implémenter le parsing de fichiers MT940
- [ ] Ajouter la génération de rapports Excel
- [ ] Mettre en place les tests automatisés

### Priorité moyenne
- [ ] Dashboard avec graphiques (Chart.js)
- [ ] Notifications par email
- [ ] Export PDF des demandes/factures
- [ ] Audit trail complet

### Priorité basse
- [ ] Interface mobile responsive
- [ ] Dark mode
- [ ] Multi-langue (EN/FR)
- [ ] Intégration calendrier

## 🤝 Collaboration

### Équipe
- Jean-Marc Roussel : Développeur principal
- François Roussel : Partenaire technologique (corporation 50-50)

### Communication
- Code reviews sur GitHub
- Documentation en français
- Réunions hebdomadaires de planification

## 📚 Ressources

### Documentation externe
- Django : https://docs.djangoproject.com/
- DRF : https://www.django-rest-framework.org/
- React : https://react.dev/
- Tailwind : https://tailwindcss.com/

### Liens internes
- Repo GitHub : https://github.com/jean385/CGTSIM
- Environnement dev : http://localhost:3000
- API dev : http://localhost:8000/api/

---

**Dernière mise à jour** : Janvier 2026
**Version** : 1.0.0
**Statut** : En développement actif
