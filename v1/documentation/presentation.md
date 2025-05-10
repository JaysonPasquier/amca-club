# American Muscle Car France - Présentation du Site Web

## Description du Site Web

Site web développé sur mesure pour l'association American Muscle Car France (AMC-F), un regroupement de passionnés de voitures américaines en France. Le client cherchait une solution numérique complète pour dynamiser sa communauté et faciliter l'organisation de ses activités.

Cette plateforme associative permet la gestion des adhérents, la promotion des événements, et la commercialisation de produits dérivés, le tout dans une interface moderne et responsive adaptée à l'image de marque de l'association.

Notre site propose :

- **Espace Événements** : Calendrier détaillé des rassemblements, meetings et sorties organisés par le club, avec possibilité de s'inscrire et de visualiser les participants
- **Boutique en Ligne** : Collection de vêtements et accessoires officiels du club, avec gestion des variations de produits (tailles, couleurs)
- **Espace Membres** : Profils personnalisés pour chaque membre, affichant leur statut dans le club et permettant l'interaction sociale
- **Forum de Discussion** : Espace d'échange entre passionnés sur différentes thématiques liées aux voitures américaines
- **Galerie Media** : Publication et partage de photos et vidéos des événements et des véhicules des membres
- **Newsletter** : Service d'abonnement pour recevoir les dernières nouvelles et annonces du club
- **À Propos** : Informations sur l'histoire et la mission du club, ainsi que les contacts des responsables

Le site est conçu pour être accessible sur tous les appareils, offrant une expérience utilisateur optimale sur ordinateurs, tablettes et smartphones.

## Technologies Utilisées

### Backend
- **Framework principal** : Django 4.2 (Python)
- **Base de données** : SQLite (développement), PostgreSQL (production)
- **API** : Django REST Framework
- **Authentification** : Système Django intégré

### Frontend
- **HTML5**, **CSS3**, **JavaScript**
- **Responsive Design** : Media queries personnalisées
- **Frameworks/Bibliothèques** :
  - Font Awesome (icônes)
  - Bootstrap 5 (via crispy_bootstrap5)

### Services Intégrés
- **Email** : SMTP via ionos.fr
- **Cartes** : Google Maps API pour la localisation des événements
- **Partage Social** : Intégration avec Facebook, Twitter, WhatsApp

### Hébergement & Déploiement
- **Hébergement** : Serveur VPS sous ionos.fr
- **Domaine** : amc-f.com
- **Serveur Web** : Nginx avec WSGI

## Palette de Couleurs

### Couleurs Principales
- **Noir** (#000000) : Couleur dominante, représentant l'élégance et la puissance
- **Bleu** (#3498db) : Couleur d'accentuation, utilisée pour les éléments interactifs
- **Gris Foncé** (#333333) : Utilisé pour les arrière-plans secondaires et la typographie
- **Rouge** (#e74c3c) : Utilisé pour les alertes et certains éléments d'action

### Couleurs Secondaires
- **Vert** (#2ecc71) : Actions positives, confirmations
- **Gris Clair** (#f5f5f5) : Arrière-plans neutres
- **Blanc** (#ffffff) : Texte et contrastes

Le design global du site s'inspire de l'esthétique automobile américaine, combinant robustesse et sophistication, avec une interface intuitive qui met en valeur le contenu et facilite la navigation pour tous les utilisateurs.
