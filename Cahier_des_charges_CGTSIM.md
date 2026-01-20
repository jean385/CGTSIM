# Cahier des Charges - Application de Gestion de Trésorerie CGTSIM

## 📋 Vue d'ensemble du projet

### Contexte
Le CGTSIM (Caisse Générale de Trésorerie des Sociétés d'Immobiliers Municipaux) gère les avances de trésorerie pour 5 CSS (Caisses de Sécurité Sociale). L'objectif est de créer une application web qui automatise la gestion des avances, le calcul des intérêts, et le suivi de la trésorerie en temps réel.

### Objectifs principaux
1. Permettre aux CSS de gérer leurs demandes d'avances en ligne
2. Automatiser les calculs d'intérêts quotidiens
3. Suivre la trésorerie et les besoins de financement en temps réel
4. Calculer et afficher les marges de profit
5. Connecter éventuellement les comptes bancaires pour un suivi automatisé

---

## 🏗️ Architecture technique recommandée

### Stack technologique

**Backend:**
- **Framework:** Django 5.0+ (Python)
  - Pourquoi ? Robuste, bien documenté, admin intégré, sécurité forte
- **Base de données:** PostgreSQL 15+
  - Pourquoi ? Fiabilité, gestion des dates/timestamps excellente, calculs financiers précis
- **API:** Django REST Framework (DRF)
  - Pour les communications frontend/backend

**Frontend:**
- **Framework:** React 18+ avec Next.js 14+
  - Pourquoi ? Interface moderne, réactive, facile à maintenir
- **UI Library:** shadcn/ui + Tailwind CSS
  - Design professionnel rapidement
- **Charts:** Recharts ou Chart.js
  - Pour les dashboards et graphiques

**Infrastructure:**
- **Serveur:** Linux (Ubuntu 22.04 LTS)
- **Web Server:** Nginx
- **Déploiement:** Docker + Docker Compose (pour simplifier)
- **Stockage fichiers:** AWS S3 ou stockage local sécurisé

**Sécurité:**
- HTTPS obligatoire (certificat SSL)
- Authentification JWT (JSON Web Tokens)
- 2FA (Two-Factor Authentication) via email ou SMS
- Encryption des données sensibles au repos

---

## 📊 Modèle de base de données

### Tables principales

#### 1. **Users (Utilisateurs)**
```
id (PK)
username
email
password_hash
first_name
last_name
role (ENUM: 'admin_cgtsim', 'user_css', 'viewer')
css_id (FK vers CSS) - NULL si admin CGTSIM
is_active
two_fa_enabled
two_fa_secret
created_at
updated_at
last_login
```

#### 2. **CSS (Caisses de Sécurité Sociale)**
```
id (PK)
code (unique, ex: 'CSS001')
name (nom complet)
address
contact_person
contact_email
contact_phone
is_active
credit_limit (limite d'avance autorisée)
default_interest_rate (taux par défaut)
created_at
updated_at
```

#### 3. **Avances (Avances aux CSS)**
```
id (PK)
css_id (FK vers CSS)
reference_number (unique, auto-généré)
amount (montant de l'avance)
start_date (date de début)
end_date (date de fin prévue) - NULL si indéterminée
actual_end_date (date de remboursement réel)
interest_rate (taux applicable)
status (ENUM: 'pending', 'approved', 'active', 'closed', 'rejected')
purpose (motif de l'avance)
approved_by (FK vers Users) - admin qui a approuvé
approved_at
created_by (FK vers Users)
created_at
updated_at
notes
```

#### 4. **Demandes_Avances (Demandes en attente)**
```
id (PK)
css_id (FK vers CSS)
requested_by (FK vers Users)
requested_amount
requested_date (date souhaitée des fonds)
purpose
justification_document (path vers fichier)
status (ENUM: 'pending', 'approved', 'rejected', 'withdrawn')
reviewed_by (FK vers Users)
reviewed_at
review_notes
created_at
updated_at
```

#### 5. **Interets_Avances (Calculs quotidiens des intérêts CSS)**
```
id (PK)
avance_id (FK vers Avances)
calculation_date (date du calcul)
outstanding_balance (solde du jour)
daily_rate (taux quotidien appliqué)
interest_amount (intérêt du jour)
cumulative_interest (intérêts cumulés à cette date)
created_at
```

#### 6. **Emprunts_Banque (Emprunts marché monétaire)**
```
id (PK)
reference_number (unique)
bank_name (nom de la banque)
amount (montant emprunté)
start_date
end_date
maturity_date
interest_rate (taux effectif)
status (ENUM: 'active', 'closed', 'refinanced')
purpose
created_at
updated_at
notes
```

#### 7. **Interets_Emprunts (Coûts des emprunts)**
```
id (PK)
emprunt_id (FK vers Emprunts_Banque)
calculation_date
outstanding_balance
daily_rate
interest_amount
cumulative_interest
created_at
```

#### 8. **Comptes_Bancaires (Comptes du CGTSIM)**
```
id (PK)
account_number
bank_name
account_type (ENUM: 'checking', 'savings', 'money_market')
currency (défaut: 'CAD')
is_active
created_at
updated_at
```

#### 9. **Soldes_Quotidiens (Soldes journaliers des comptes)**
```
id (PK)
compte_id (FK vers Comptes_Bancaires)
balance_date
opening_balance
closing_balance
interest_earned (intérêts gagnés ce jour)
source (ENUM: 'manual', 'import_csv', 'api_bank')
imported_at
created_at
```

#### 10. **Transactions_Bancaires (Mouvements bancaires)**
```
id (PK)
compte_id (FK vers Comptes_Bancaires)
transaction_date
value_date
description
debit_amount
credit_amount
balance_after
reference_number
transaction_type (ENUM: 'avance_css', 'remboursement_css', 'emprunt_banque', 'remboursement_emprunt', 'interet', 'autre')
related_avance_id (FK vers Avances) - NULL si non applicable
related_emprunt_id (FK vers Emprunts_Banque) - NULL
created_at
```

#### 11. **Parametres_Systeme (Configuration)**
```
id (PK)
key (unique, ex: 'base_interest_rate')
value
data_type (ENUM: 'string', 'number', 'boolean', 'json')
description
updated_by (FK vers Users)
updated_at
```

#### 12. **Audit_Log (Traçabilité)**
```
id (PK)
user_id (FK vers Users)
action (ex: 'create_avance', 'approve_demande', 'update_rate')
table_name
record_id
old_values (JSON)
new_values (JSON)
ip_address
created_at
```

---

## 🎯 Plan de développement par phases

### **PHASE 1 - MVP (Minimum Viable Product)** ⏱️ 8-12 semaines

#### Objectifs Phase 1
- Portail CSS fonctionnel de base
- Gestion manuelle des avances par CGTSIM
- Calculs d'intérêts automatisés
- Dashboard CGTSIM basique
- Import manuel des soldes bancaires

#### Fonctionnalités Phase 1

**1. Authentification & Gestion utilisateurs (Semaine 1-2)**
- Login/Logout sécurisé
- Gestion des mots de passe (reset, changement)
- Création de comptes CSS par admin
- Rôles et permissions de base

**2. Portail CSS (Semaine 3-4)**
- Dashboard CSS :
  - Avances en cours (montant, date début, solde, intérêts courus)
  - Historique des avances
  - Solde d'intérêts du mois
- Simulateur d'avance :
  - Formulaire : montant + durée estimée
  - Calcul instantané des intérêts estimés
- Demande d'avance :
  - Formulaire complet (montant, date souhaitée, motif)
  - Upload de document justificatif (PDF)
  - Statut de la demande visible

**3. Backend - Gestion des avances (Semaine 5-6)**
- CRUD avances (Create, Read, Update, Delete)
- Workflow des demandes :
  - Création par CSS
  - Révision par CGTSIM
  - Approbation/Rejet
  - Notification par email
- Calcul automatique des intérêts :
  - Job quotidien (cron) à minuit
  - Formule : Intérêt = Capital × Taux × Nb_jours / 365
  - Stockage dans Interets_Avances

**4. Cockpit CGTSIM - Version basique (Semaine 7-8)**
- Liste de toutes les CSS
- Vue des avances actives par CSS
- Demandes d'avances en attente (à approuver)
- Calendrier des décaissements à venir (7 jours)
- Import manuel de soldes bancaires (CSV)
- Calcul manuel du besoin de liquidités

**5. Rapports basiques (Semaine 9-10)**
- Export Excel :
  - Avances par CSS
  - Intérêts facturés par période
  - Avances actives au [date]
- Rapport mensuel automatique (PDF) :
  - Résumé des avances
  - Intérêts générés
  - Par CSS

**6. Tests & Déploiement (Semaine 11-12)**
- Tests unitaires backend
- Tests d'intégration
- Tests utilisateurs (2-3 CSS pilotes)
- Corrections de bugs
- Déploiement en production
- Documentation utilisateur

#### Livrables Phase 1
✅ Application web déployée et accessible
✅ 5 comptes CSS créés et fonctionnels
✅ Calculs d'intérêts automatiques quotidiens
✅ Rapports mensuels exportables
✅ Manuel utilisateur (CSS + CGTSIM)

---

### **PHASE 2 - Optimisations & Automatisation** ⏱️ 10-14 semaines

#### Objectifs Phase 2
- Gestion des emprunts marché monétaire
- Connexion bancaire automatisée
- Calcul de marge en temps réel
- Dashboards avancés
- 2FA et sécurité renforcée

#### Fonctionnalités Phase 2

**1. Gestion des emprunts banque (Semaine 13-14)**
- CRUD emprunts marché monétaire
- Calcul automatique des intérêts sur emprunts
- Association emprunts ↔ avances CSS
- Vue du coût réel de financement

**2. Connexion bancaire (Semaine 15-18)**
- **Option A - Import automatisé :**
  - Import CSV/MT940 via SFTP ou upload
  - Parsing automatique des transactions
  - Réconciliation avec avances/emprunts
- **Option B - API bancaire (si disponible) :**
  - Intégration API de la banque
  - Récupération quotidienne automatique des soldes
  - Récupération des transactions
- Tableau de soldes quotidiens multi-comptes
- Alertes si solde < seuil critique

**3. Calcul de besoin de liquidités (Semaine 19-20)**
- Calendrier prévisionnel :
  - Décaissements aux CSS (7-30 jours)
  - Remboursements attendus
  - Échéances emprunts banque
- Calcul automatique :
  - Solde projeté jour par jour
  - Besoin net de financement
  - Suggestions d'emprunts marché monétaire

**4. Calcul de marge & Analytics (Semaine 21-23)**
- Dashboard CGTSIM avancé :
  - Marge par CSS (intérêts facturés - coût financement)
  - Marge globale du mois/trimestre/année
  - Graphiques évolution dans le temps
  - Top CSS par rentabilité
  - Analyse par type de produit
- Indicateurs clés (KPIs) :
  - ROA (Return on Assets)
  - Spread moyen (taux CSS - taux emprunts)
  - Volume total d'avances
  - Taux d'utilisation de la capacité

**5. Sécurité renforcée (Semaine 24)**
- 2FA obligatoire pour admins CGTSIM
- 2FA optionnel pour CSS
- Logs d'audit détaillés
- Alertes de sécurité (tentatives connexion échouées)
- Backup automatique quotidien de la DB

**6. Notifications & Alertes (Semaine 25-26)**
- Notifications email :
  - Demande d'avance soumise (à CSS et CGTSIM)
  - Demande approuvée/rejetée
  - Rappel de remboursement
  - Intérêts facturés mensuellement
- Alertes internes CGTSIM :
  - Besoin de liquidités imminent
  - Solde bancaire faible
  - Avance dépassant la limite CSS
  - Erreur dans calcul d'intérêts

#### Livrables Phase 2
✅ Gestion complète des emprunts banque
✅ Import/API bancaire fonctionnel
✅ Calcul de marge en temps réel
✅ Dashboards analytics avancés
✅ 2FA activé
✅ Système d'alertes opérationnel

---

## 🔐 Sécurité & Conformité

### Mesures de sécurité

1. **Authentification forte**
   - Mots de passe : minimum 12 caractères, complexité élevée
   - Hashage bcrypt (coût factor 12+)
   - 2FA via TOTP (Google Authenticator) ou SMS
   - Verrouillage après 5 tentatives échouées

2. **Autorisation**
   - RBAC (Role-Based Access Control)
   - Principe du moindre privilège
   - Séparation des rôles (CSS ne voit que ses données)

3. **Chiffrement**
   - HTTPS (TLS 1.3) obligatoire
   - Données sensibles chiffrées en DB (AES-256)
   - Tokens JWT avec expiration courte (15 min)

4. **Audit & Traçabilité**
   - Logging de toutes les actions sensibles
   - Retention des logs 7 ans minimum
   - Backup quotidien avec rétention 90 jours

5. **Protection des données**
   - Conformité RGPD/lois québécoises
   - Anonymisation des données de test
   - Politique de retention des données

### Tests de sécurité
- Penetration testing avant mise en production
- Scan de vulnérabilités (OWASP Top 10)
- Revue de code sécurité

---

## 📈 Intégration avec Excel existant

### Stratégie de migration

**Phase de transition (pendant Phase 1) :**
1. Double saisie : Excel + nouvelle app
2. Comparaison quotidienne des calculs
3. Validation par échantillonnage
4. Ajustements des formules si écarts

**Migration des données historiques :**
- Script d'import des avances passées depuis Excel
- Validation des totaux d'intérêts
- Conservation Excel en archive

**Exports réguliers :**
- Export Excel mensuel pour comptabilité
- Format compatible avec systèmes existants (DOFIN, etc.)

---

## 💾 Gestion des données bancaires

### Formats supportés

**Import manuel (Phase 1) :**
- CSV format standard
- Colonnes requises : Date, Description, Débit, Crédit, Solde
- Validation des doublons
- Réconciliation avec avances

**Import automatisé (Phase 2) :**
- MT940 (format SWIFT)
- OFX (Open Financial Exchange)
- Format propriétaire banque (si API)

### API bancaire - Considérations

Si connexion directe aux comptes bancaires :
1. **Accord formel avec la banque**
   - Demande d'accès API corporate
   - Convention de service
   - Certification sécurité

2. **Agrégateurs possibles (alternative) :**
   - Flinks (canadien)
   - Plaid (US/Canada)
   - Coût : ~500-2000$/mois selon volume

3. **Sécurité renforcée :**
   - Tokens API sécurisés
   - IP whitelisting
   - Encryption bout-en-bout

---

## 🚀 Déploiement & Infrastructure

### Environnements

**Développement (Dev) :**
- Machine locale de ton frère
- Docker Compose
- Base de données de test

**Staging (Test) :**
- Serveur de pré-production
- Données anonymisées
- Tests utilisateurs

**Production (Prod) :**
- Serveur dédié ou cloud
- Haute disponibilité
- Backups automatiques

### Hébergement recommandé

**Option 1 - Serveur dédié interne CGTSIM :**
- Avantages : Contrôle total, conformité
- Inconvénients : Maintenance, coûts hardware

**Option 2 - Cloud (AWS, Azure, Google Cloud) :**
- Avantages : Scalabilité, backups automatiques
- Inconvénients : Coûts récurrents (~200-500$/mois)
- Recommandé : Région Canada (lois québécoises)

**Option 3 - Hybrid :**
- App sur cloud
- Base de données on-premise
- VPN sécurisé

### Configuration serveur minimale

**Phase 1 :**
- 4 CPU cores
- 8 GB RAM
- 100 GB SSD
- Bande passante : 1 TB/mois

**Phase 2 (avec API bancaire) :**
- 8 CPU cores
- 16 GB RAM
- 200 GB SSD
- Bande passante : 2 TB/mois

---

## 📚 Formation & Documentation

### Documentation technique (pour développeurs)

1. **Architecture Diagram**
   - Schéma de la base de données
   - Flux de données
   - API endpoints

2. **Code Documentation**
   - Docstrings Python (PEP 257)
   - Comments dans le code
   - README complet

3. **Setup Guide**
   - Installation environnement dev
   - Configuration variables d'environnement
   - Scripts de déploiement

### Documentation utilisateur

**Pour les CSS :**
- Guide de connexion
- Comment faire une demande d'avance
- Lecture du dashboard
- FAQ

**Pour CGTSIM :**
- Gestion des demandes
- Approbation d'avances
- Lecture des rapports
- Import de données bancaires
- Résolution de problèmes

### Formation

**Phase 1 :**
- Session 2h pour admins CGTSIM
- Session 1h pour chaque CSS (vidéo + live)

**Phase 2 :**
- Session 1h nouvelles fonctionnalités
- Documentation vidéo mise à jour

---

## 💰 Estimation budgétaire

### Coûts de développement (si ton frère fait tout)

**Phase 1 (8-12 semaines) :**
- Développement : 300-500 heures
- À ~50-80$/h freelance : 15 000 - 40 000$
- *Si ton frère = gratuit ou arrangement familial : 0-10 000$ en outils/licences*

**Phase 2 (10-14 semaines) :**
- Développement : 400-600 heures
- À 50-80$/h : 20 000 - 48 000$
- *Si ton frère : 0-15 000$ outils/API bancaire*

### Coûts d'infrastructure annuels

**Hébergement cloud (estimé) :**
- Serveur : 200-400$/mois = 2 400 - 4 800$/an
- Base de données : 100-200$/mois = 1 200 - 2 400$/an
- Stockage/Backup : 50$/mois = 600$/an
- **Total hébergement : 4 200 - 7 800$/an**

**Licences/Services :**
- Certificat SSL : 0$ (Let's Encrypt gratuit)
- Email (SendGrid) : 20$/mois = 240$/an
- API bancaire (si applicable) : 500-2000$/mois = 6 000 - 24 000$/an
- Monitoring (Sentry) : 30$/mois = 360$/an
- **Total licences : 6 600 - 24 600$/an**

**Maintenance annuelle :**
- Support technique : 5 000 - 10 000$/an
- Mises à jour sécurité : inclus
- **Total maintenance : 5 000 - 10 000$/an**

### Budget total estimé (3 ans)

**Scénario conservateur (développement familial) :**
- Phase 1 : 10 000$
- Phase 2 : 15 000$
- Infrastructure (3 ans × 5 000$) : 15 000$
- Maintenance (3 ans × 7 000$) : 21 000$
- **TOTAL 3 ans : ~60 000 - 80 000$**

**Scénario avec développeur externe :**
- Phase 1 + 2 : 60 000 - 90 000$
- Infrastructure (3 ans) : 15 000 - 25 000$
- Maintenance (3 ans) : 21 000 - 30 000$
- **TOTAL 3 ans : ~100 000 - 150 000$**

---

## 📊 ROI attendu

### Gains quantifiables

**Gains de temps :**
- Calculs manuels Excel : ~10h/semaine actuellement
- Après automatisation : ~2h/semaine
- **= 8h × 50 semaines × 50$/h = 20 000$/an**

**Réduction d'erreurs :**
- Erreurs de calcul : 2-3 par mois actuellement (estimé)
- Impact moyen par erreur : 500-2000$ (ajustements, temps perdu)
- **= 12 000 - 72 000$/an évité**

**Optimisation trésorerie :**
- Meilleure visibilité = emprunts mieux timés
- Réduction coût emprunt : 0.1-0.2% sur volume
- Si 50M$ d'avances/an : **= 50 000 - 100 000$/an**

**Total gains annuels estimés : 80 000 - 190 000$/an**

**ROI :**
- Investissement : 60 000 - 150 000$
- Retour année 1 : 80 000 - 190 000$
- **Payback : 4-18 mois**

---

## ⚠️ Risques & Mitigation

### Risques techniques

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Bugs dans calculs d'intérêts | Haut | Moyen | Double validation avec Excel pendant 3 mois |
| Downtime serveur | Moyen | Faible | Backups quotidiens, monitoring 24/7 |
| Faille de sécurité | Haut | Faible | Audit sécurité, penetration test |
| Problème API bancaire | Moyen | Moyen | Fallback sur import manuel CSV |

### Risques organisationnels

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Résistance au changement CSS | Moyen | Moyen | Formation, support dédié, phase pilote |
| Manque de ressources dev | Haut | Moyen | Découpage en phases, priorisation |
| Dépassement budget | Moyen | Moyen | Budget buffer 20%, validation étapes |
| Non-conformité réglementaire | Haut | Faible | Validation légale MEQ, audit conformité |

---

## 🛠️ Outils de développement recommandés

### Pour ton frère développeur

**IDE :**
- Visual Studio Code (gratuit)
- Extensions : Python, Django, ESLint, Prettier

**Gestion de version :**
- Git + GitHub ou GitLab (privé)
- Branching strategy : Git Flow

**Base de données :**
- pgAdmin 4 (GUI pour PostgreSQL)
- DBeaver (alternative)

**API Testing :**
- Postman (gratuit)
- Thunder Client (extension VS Code)

**Monitoring (Phase 2) :**
- Sentry (erreurs)
- New Relic ou Datadog (performance)

---

## 📞 Prochaines étapes concrètes

### Semaine 1-2 : Préparation

1. **Validation du cahier des charges**
   - Revue avec équipe CGTSIM
   - Ajustements si nécessaire
   - Approbation formelle

2. **Setup environnement développement**
   - Installation Docker, PostgreSQL, Django
   - Création repo Git
   - Structure de base du projet

3. **Kickoff meeting**
   - Toi + ton frère + équipe
   - Présentation du plan Phase 1
   - Définition des priorités

### Semaine 3 : Démarrage développement

1. **Sprint 1 : Base de données + Auth**
   - Création des modèles Django
   - Migrations DB
   - Système de login

2. **Communication régulière**
   - Point hebdomadaire (1h)
   - Partage d'écran pour démos
   - Slack ou Teams pour questions

---

## 📝 Annexes

### A. Formules de calcul d'intérêts

**Intérêt quotidien (méthode 365 jours) :**
```
Intérêt_jour = Capital × (Taux_annuel / 365)
```

**Intérêt sur période :**
```
Intérêt_période = Capital × Taux_annuel × (Nb_jours / 365)
```

**Intérêt composé (si applicable) :**
```
Montant_final = Capital × (1 + Taux_annuel)^(Nb_jours/365)
Intérêt_composé = Montant_final - Capital
```

### B. Exemple de workflow demande d'avance

```
1. CSS crée demande → Statut = "pending"
   ↓
2. Email automatique à CGTSIM
   ↓
3. Admin CGTSIM révise demande
   ↓
4. Approbation → Statut = "approved"
   OU Rejet → Statut = "rejected"
   ↓
5. Si approuvé → Création Avance (statut = "active")
   ↓
6. Email à CSS confirmation
   ↓
7. Décaissement effectué (transaction bancaire)
   ↓
8. Calcul intérêts quotidiens démarre
```

### C. Checklist sécurité pré-production

- [ ] Tous les mots de passe en environnement variables
- [ ] HTTPS activé avec certificat valide
- [ ] 2FA testé et fonctionnel
- [ ] Backup automatique configuré et testé
- [ ] Logs d'audit activés
- [ ] Scan de vulnérabilités effectué
- [ ] Penetration test réalisé
- [ ] Plan de disaster recovery documenté
- [ ] Formation sécurité donnée aux admins
- [ ] Politique de mots de passe appliquée

### D. KPIs à suivre post-lancement

**Techniques :**
- Uptime (objectif : 99.5%+)
- Temps de réponse moyen (< 2 secondes)
- Nombre d'erreurs/jour (< 5)

**Fonctionnels :**
- Nombre de demandes d'avances/mois
- Délai moyen approbation (objectif : < 24h)
- Taux d'utilisation CSS (% qui utilisent régulièrement)

**Financiers :**
- Volume total d'avances
- Marge moyenne par CSS
- Coût moyen de financement

---

## ✅ Conclusion

Ce cahier des charges te donne une roadmap complète pour développer ton application CGTSIM. Avec ton frère comme développeur et un développement en 2 phases, tu auras :

**En 3 mois (Phase 1) :**
- Un système fonctionnel de base
- Automatisation des calculs
- Portail CSS opérationnel

**En 6-7 mois (Phase 2) :**
- Système complet avec connexion bancaire
- Analytics avancés
- ROI positif dès la première année

**Points clés de succès :**
1. Commencer simple (Phase 1 MVP)
2. Tester avec 1-2 CSS pilotes
3. Itérer selon feedback
4. Documenter au fur et à mesure
5. Prioriser la sécurité dès le début

Si tu as des questions sur n'importe quelle section, n'hésite pas ! Je peux aussi te créer des documents plus détaillés sur des aspects spécifiques (structure DB, API endpoints, etc.).

Bonne chance avec le projet ! 🚀
