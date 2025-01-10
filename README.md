![image](https://github.com/user-attachments/assets/f883ed51-6f59-4e6a-a4c4-7275fd678782)


# Analyse Data App

Ce projet est une application Django pour l'analyse et la visualisation des données. Il comprend des fonctionnalités pour le téléchargement, la visualisation, et l'analyse des données via des interfaces conviviales.

## Structure du projet

```
analyse-data-app/
├── manage.py
├── app/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index_data.html
│   │   ├── analyse_data.html
│   │   ├── upload_data.html
│   │   ├── view_data.html
│   │   ├── visualize_data.html
│   ├── static/
│   ├── views.py
│   ├── urls.py
│   └── models.py
├── requirements.txt
└── README.md
```

## Fonctionnalités principales

1. **Page d'accueil** :
   - Présente un aperçu des fonctionnalités de l'application (gérée par `index_data`).

2. **Téléchargement des données** :
   - Permet aux utilisateurs de télécharger des fichiers de données via une interface web conviviale (gérée par `upload_data`).

3. **Visualisation des données** :
   - Permet d'afficher les données téléchargées sous forme de tableau ou de graphique (gérée par `view_data` et `visualize_data`).

4. **Analyse des données** :
   - Effectue des analyses sur les ensembles de données chargés, par exemple des statistiques descriptives ou des modèles d'apprentissage machine (gérée par `analyse_data`).

## Prérequis

- Python 3.8 ou supérieur
- Django 4.x ou supérieur
- Librairies listées dans `requirements.txt`

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/YoussefMouchou/Data-Analyste-project-with-django.git
   cd analyse_project
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Appliquez les migrations :
   ```bash
   python manage.py migrate
   ```

4. Lancez le serveur de développement :
   ```bash
   python manage.py runserver
   ```

## Utilisation

1. Accédez à l'application dans votre navigateur à `http://127.0.0.1:8000/`.
2. Naviguez entre les pages suivantes :
   - **Accueil** : Page principale de l'application (`index_data`).
   - **Téléchargement des données** : Page pour télécharger un fichier de données.
   - **Visualisation des données** : Page pour afficher les données téléchargées.
   - **Analyse des données** : Page pour effectuer des analyses sur les données.



