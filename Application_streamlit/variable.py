# FICHIER CONTENANT LES VARIABLES QUI SE RÉPÈTENT ENTRE PLUSIEURS PAGES


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import pandas as pd
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Définitions des variables


# Variable qui permet de définir le nombre d'events suivant les centres que l'on souhaite étudier
nb_events_suivant = 5

# Dictionnaire contenant pour chaque saison le classement de ligue 2 avec les noms d'équipe au format Skill Corner
dico_rank_SK = {
    "2023/2024" : ["AJ Auxerre", "Angers SCO", "AS Saint-Étienne", "Rodez Aveyron", "Paris FC", "SM Caen",
                   "Stade Lavallois Mayenne FC", "Amiens Sporting Club", "En Avant de Guingamp", "Pau FC", "Grenoble Foot 38",
                   "Girondins de Bordeaux", "SC Bastia", "FC Annecy", "AC Ajaccio", "Dunkerque", "ES Troyes AC", "US Quevilly-Rouen",
                   "US Concarneau", "Valenciennes FC"]
                   }


# Dictionnaire contenant pour chaque saison le classement de ligue 2 avec les noms d'équipe au format Stats Bomb
dico_classement_SB = {
    "2023/2024" : [131, 129, 153, 143, 136, 137, 168, 147, 156, 134, 130, 139, 138, 144, 164, 141, 165, 152]
                   }


# Dataframe permettant le choix de la taille des différents groupes d'équipes
taille_groupes = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])
taille_groupes["Slider"] = "Nombre d'équipe dans le " + taille_groupes.index


# Mise en forme du texte des heatmaps des les zones de début d'action
path_effect_1 = [path_effects.Stroke(linewidth=1, foreground='black'), path_effects.Normal()]

# Mise en forme du texte des heatmaps pour les zones de tir et de centre
path_effect_2 = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]

# Colormap des heatmaps de gauche
colormapred = LinearSegmentedColormap.from_list('custom_cmap', [(1, 1, 1), (198/255, 11/255, 70/255)])

# Colormap des heatmaps de droite
colormapblue = LinearSegmentedColormap.from_list('custom_cmap', [(1, 1, 1), (0, 45/255, 106/255)])

# Dictionnaire pour l'affichage des titres des heatmaps
dico_label = {"Choisir Top/Middle/Bottom" : ["du"], "Choisir équipe" : ["de"]}