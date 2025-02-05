# Comment prendre en main le projet ?

## 1) Faire fonctionner l'application avec Docker


## 2) Utiliser et modifier les différents programmes du projet
Si vous souhaitez rentrer au coeur de ce projet et modifier les programmes liés à l'application Streamlit ou au traitement des donneés, alors il faudra suivre certaines étapes afin de faire fonctionner le projet.

Ce projet est séparé en 2 principales parties : l'application Streamlit et le traitement des données, qui sont en réalités deux dossiers présents à la racine du projet.

En effet, nous sommes parties de données brutes fournies par le Clermont Foot 63, que nous avons traitées/transformées à l'aide de codes Python et Jupyter Notebook afin d'en extraire des informations.

Ce sont ces données traitées qui sont utilisées pour faire fonctionner l'application Streamlit.

Pour chacune de ces deux parties, nous avons travaillé avec un environnement virtuel (il y en a donc un par dossier/partie).  
Cependant, nous avons passé ces environnements dans le fichier "gitignore", il est donc important de les installer après avoir récupéré le repository du projet sur son PC.  
Pour ce faire, nous avons créé des fichiers "requirements.txt" pour chacun des environnements.

⚠️ Il faut travailler avec la version 3.12.6 de Python.

Pour réaliser les différentes étapes que nous allons expliquées, nous vous conseillons d'utiliser l'éditeur VS Code, qui offre de nombreuses extensions pratiques telles que GitHub, Docker, etc.

Voici les étapes à suivre pour mettre en place les environnements virtuels :

### A) Traitement des données

1) Ouvrir un terminal de commande (par exemple celui dans VS Code)
2) Se déplacer dans le dossier "Traitement_donnees" à l'aide de la commande "cd"
3) Créer dans ce dossier "Traitement_donnees" l'environnement virtuel vide : python -m venv env_traitement
4) Activer l'environnement virtuel : env_traitement\Scripts\activate
5) Installer les librairies présentes dans le fichier requirements.txt : pip install -r .\requirements.txt
6) Ajouter l'environnement virtuel comme noyau Jupyter (en effet, nous travaillons avec des scripts Jupyter Notebook) : python -m ipykernel install --user --name=env_traitement --display-name "Python (env_traitement)"
7) Pour l'ensemble des scripts Jupyter Notebook de ce dossier, sélectionner l'environnement virtuel "env_traitement" comme noyau
