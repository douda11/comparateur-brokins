# Comparateur Brokins

## Description
Application Flask pour la comparaison d'assurances avec extraction de données PDF utilisant l'IA.

## Fonctionnalités
- 🔍 Extraction automatique de données depuis les PDF d'assurance
- 📊 Comparaison intelligente des contrats d'assurance
- 🤖 Utilisation de l'IA pour l'analyse des documents
- 📋 Interface web intuitive pour la gestion des contrats

## Technologies utilisées
- **Backend**: Python Flask
- **IA**: Extraction de données PDF
- **Frontend**: HTML, CSS, JavaScript
- **Base de données**: JSON (contracts.json)

## Installation

### Prérequis
- Python 3.8+
- pip

### Étapes d'installation

1. Cloner le repository
```bash
git clone https://github.com/douda11/comparateur-brokins.git
cd comparateur-brokins
```

2. Créer un environnement virtuel
```bash
python -m venv comparateurvenv
```

3. Activer l'environnement virtuel
```bash
# Windows
comparateurvenv\Scripts\activate

# Linux/Mac
source comparateurvenv/bin/activate
```

4. Installer les dépendances
```bash
pip install -r requirements.txt
```

5. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer le fichier .env avec vos configurations
```

## Utilisation

1. Démarrer l'application
```bash
python app.py
```

2. Ouvrir votre navigateur et aller à `http://127.0.0.1:5000`

3. Utiliser l'interface pour :
   - Télécharger des PDF d'assurance
   - Extraire les données automatiquement
   - Comparer les différents contrats

## Structure du projet
```
comparateur_brokins/
├── app.py                 # Application Flask principale
├── comparateur.py         # Logique de comparaison
├── pdf_json.py           # Extraction PDF vers JSON
├── delete_contract.py    # Gestion suppression contrats
├── requirements.txt      # Dépendances Python
├── contracts.json        # Base de données des contrats
├── examples.json         # Exemples de données
├── regles.pdf           # Règles de comparaison
├── static/              # Fichiers CSS/JS
├── templates/           # Templates HTML
├── uploads/             # Dossier des fichiers uploadés
└── extractions/         # Données extraites des PDF
```

## API Endpoints

### Comparaison
- `POST /compare` - Comparer des contrats d'assurance

### Extraction
- `POST /extract` - Extraire des données depuis un PDF

## Contribution
1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact
- **Développeur**: douda11
- **GitHub**: https://github.com/douda11/
- **Email**: hedibenmessaoud1110@gmail.com

## Changelog
### v1.0.0 (2025-09-23)
- Version initiale
- Extraction PDF avec IA
- Interface de comparaison
- Gestion des contrats JSON
