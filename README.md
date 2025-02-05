# Comment prendre en main le projet ?

## 1) Faire fonctionner l'application avec Docker


## 2) Utiliser et modifier les différents programmes du projet
Si vous souhaitez rentrer au coeur de ce projet et modifier les programmes liés à l'application Streamlit ou au traitement des données, alors il faudra suivre certaines étapes afin de faire fonctionner le projet.

Ce projet est séparé en 2 principales parties : l'application Streamlit et le traitement des données, qui sont en réalité deux dossiers présents à la racine du projet.

En effet, nous sommes partis de données brutes fournies par le Clermont Foot 63, que nous avons traitées et transformées à l'aide de codes Python et Jupyter Notebook afin d'en extraire des informations.

Ce sont ces données traitées qui sont utilisées pour faire fonctionner l'application Streamlit.

Pour chacune de ces deux parties, nous avons travaillé avec un environnement virtuel (il y en a donc un par dossier/partie).  
Cependant, nous avons passé ces environnements dans le fichier "gitignore", il est donc important de les installer après avoir récupéré le repository du projet sur son PC.  
Pour ce faire, nous avons créé des fichiers "requirements.txt" pour chacun des environnements.

⚠️ Il faut travailler avec la version 3.12.6 de Python.

Pour réaliser les différentes étapes que nous allons expliquées, nous vous conseillons d'utiliser l'éditeur VS Code, qui offre de nombreuses extensions pratiques telles que GitHub, Docker, etc.

Voici les étapes à suivre pour mettre en place les environnements virtuels :

### A) Traitement des données

1) Ouvrir un terminal de commande (par exemple celui dans VS Code)
2) Se déplacer dans le dossier "Traitement_donnees" à l'aide de la commande "cd" (cf. image1 pour voir à quoi doit ressembler le terminal)
3) Créer dans ce dossier "Traitement_donnees" l'environnement virtuel vide : python -m venv env_traitement
4) Activer l'environnement virtuel : env_traitement\Scripts\activate
5) Installer les librairies présentes dans le fichier requirements.txt : pip install -r .\requirements.txt
6) Ajouter l'environnement virtuel comme noyau Jupyter (en effet, nous travaillons avec des scripts Jupyter Notebook) : python -m ipykernel install --user --name=env_traitement --display-name "Python (env_traitement)"
7) Pour l'ensemble des scripts Jupyter Notebook de ce dossier, sélectionner l'environnement virtuel "env_traitement" comme noyau.  
Pour ce faire, pour chaque fichier ".ipynb", il faut :
a) Ouvir le script (dans VS Code)
b) Cliquer sur "Detecting Kernels" en haut à droite (cf. image2)
c) Cliquer sur "Select Another Kernel..."
d) Cliquer sur "Jupyter Kernel..."
e) Si l'environnement "Python (env_traitement)" ne s'affiche pas, appuyer sur le bouton pour rafraichir la liste des environnements. Sinon, essayer de fermer le projet, relancer VS Code, et réessayer.
f) Sélectionner l'environnement "Python (env_traitement)"

Après avoir réalisé toutes ces étapes, vous devriez être en mesure d'exécuter tous les scripts de ce dossier, de les modifier, etc.

### B) Application Streamlit

1) Ouvrir un terminal de commande (par exemple celui dans VS Code)
2) Se déplacer dans le dossier "Application_streamlit" à l'aide de la commande "cd"
3) Créer dans ce dossier "Application_streamlit" l'environnement virtuel vide : python -m venv env_app
4) Activer l'environnement virtuel : env_app\Scripts\activate
5) Installer les librairies présentes dans le fichier requirements.txt : pip install -r .\requirements.txt
6) Ajouter l'environnement virtuel comme noyau Jupyter : python -m ipykernel install --user --name=env_app --display-name "Python (env_app)"
7) Pour l'ensemble des scripts Python (nous travaillons avec des fichiers ".py" pour cette partie), sélectionner cet environnement comme interpreteur :
a) Cliquer sur "view" en haut de l'écran (cf. image3) et sélectionner "Command Palette..."
b) Chercher et sélectionner "Python: Select Interpreter"
c) Cliquer sur "Enter interpreter path..."
d) Entrer : "Application_streamlit\env_app\Scripts\python.exe"

Après avoir réalisé toutes ces étapes, vous devriez être en mesure d'exécuter tous les scripts de ce dossier, de les modifier, etc.
