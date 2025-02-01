# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 1) Importation des bibliothèques, fonctions et variables


import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import sqlite3
from functools import partial

from fonction import execute_SQL, load_session_state, key_widg, init_session_state, filtre_session_state, push_session_state, get_session_state, heatmap_centre
from variable import dico_classement_SB, dico_label, taille_groupes, nb_events_suivant

# Index slicer pour la sélection de donnée sur les dataframes avec multi-index
idx = pd.IndexSlice


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 2) Connexion à la base de données traitées "database.db"


connect = sqlite3.connect("Databases/database.db")
cursor = connect.cursor()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 3) Mise en page de la page


# Largeur de la page
st.set_page_config(layout="wide")

# Titre de la page
st.title("Zones de centre")

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 4) Définition des fonctions de mofication du session state


load_session_state = partial(load_session_state, suffixe = "_zone_centre")
key_widg = partial(key_widg, suffixe = "_zone_centre")
get_session_state = partial(get_session_state, suffixe = "_zone_centre")
init_session_state = partial(init_session_state, suffixe = "_zone_centre")
push_session_state = partial(push_session_state, suffixe = "_zone_centre")
filtre_session_state = partial(filtre_session_state, suffixe = "_zone_centre")


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 5) Choix de la compétition, de la saison et du groupe à afficher


columns = st.columns([2, 4, 3], vertical_alignment = "center", gap = "large")

# Importation de l'ensemble des compétitions disponibles dans les données "zones_de_centre" dans la liste "liste_compet"
params = []
stat = f"SELECT DISTINCT Compétition FROM zones_de_centre"
liste_compet, desc = execute_SQL(cursor, stat, params)
liste_compet = [i[0] for i in liste_compet]

# Choix de la compétition via la variable "choix_compet"
with columns[0] :
    load_session_state("Compétition")
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, **key_widg("Compétition"))

# Importation de l'ensemble des saisons disponibles pour la compétition choisie dans les données "zones_de_centre" dans la liste "liste_saisons"
params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM zones_de_centre WHERE Compétition = ?"
liste_saisons, desc = execute_SQL(cursor, stat, params)
liste_saisons = [i[0] for i in liste_saisons]

# Choix de la ou des saisons via la variable "choix_saisons"
with columns[1] :
    init_session_state("Saison", [max(liste_saisons)])
    load_session_state("Saison")
    choix_saisons = st.multiselect("Choisir saisons", liste_saisons, **key_widg("Saison"))

# On choisit si on veut étudier les zones de centre pour des équipes (à sélectionner) ou pour des groupes d'équipes.
# Le choix est stocké dans la variable "choix_categorie"
with columns[2] :
    load_session_state("Groupe")
    choix_categorie = st.radio("Choix groupe", ["Choisir Top/Middle/Bottom", "Choisir équipe"], label_visibility = "hidden",
                            **key_widg("Groupe"))

# Arrêt du programme dans le cas ou aucune saison n'a été sélectionnée
if len(choix_saisons) == 0 :
    st.stop()

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 6) Importation de l'ensemble des données "zones_de_centre" après avoir filtré la compétition et la ou les saisons souhaitées


# Création du dataframe contenant les données importées
params = [choix_compet] + choix_saisons
stat = f"SELECT * FROM zones_de_centre WHERE Compétition = ? and Saison IN ({', '.join('?' * len(choix_saisons))})"
res, desc = execute_SQL(cursor, stat, params)
zones_de_centre = pd.DataFrame(res)
zones_de_centre.columns = [i[0] for i in desc]

# Suppression des colonnes "Compétition" et "index" qui ne nous sont pas utiles
zones_de_centre.drop(["Compétition", "index"], axis = 1, inplace = True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 7) a) Choix de la tailles des groupes "Top", "Middle" et "Bottom" dans le cas ou l'utilisateur a décidé d'étudier des groupes d'équipes

# L'utilisateur pourra choisir la taille du "Top" et du "Bottom", et on en déduira la taille du "Middle" :
# taille "Middle" = nombre d'équipes - taille "Top" - taille "Bottom".
# Il est important de noté que le nombre d'équipes d'une compétition dépend de la saison. Par exemple, il y avait 20 équipes en Ligue 1
# lors de la saison 2022/2023 et 18 lors de la saison 2023/2024

# Lorsque l'utilisateur a sélectionné plusieurs saisons ayant un nombre d'équipes différent (par exemple 18 et 20), alors la taille 
# maximale du groupe "Top" qu'il pourra choisir sera égale au nombre minimum d'équipes de l'ensemble des saisons (donc 18)
# Ensuite, si l'utilisateur choisi la taille maximale pour le groupe "Top" (donc 18), alors on considèrera qu'il a choisi l'ensemble des
# équipes pour l'ensemble des saisons (donc 18 équipes pour les saisons à 18 équipes et 20 équipes pour les saisons à 20 équipes)

# On va stocker les choix de l'utilisateur pour la taille des groupes dans le dataframe "taille_groupes"

if choix_categorie == "Choisir Top/Middle/Bottom" :
    # Création d'une Série contenant le nombre d'équipes pour chaque saison sélectionnée
    nb_team_saison = zones_de_centre[["Saison", "Équipe"]].drop_duplicates().groupby("Saison").apply(len)

    # On détermine la taille maximale du groupe "Top"
    max_nb_team_saison = min(nb_team_saison)

    columns = st.columns(3, gap = "large", vertical_alignment = "center")

    # Choix de la taille du "Top", qui possède au moins une équipe
    with columns[0] :
        load_session_state("taille_top")
        taille_groupes.loc["Top", "Taille"] = st.slider(taille_groupes.loc["Top", "Slider"], min_value = 1,
                max_value = max_nb_team_saison, **key_widg("taille_top"))    

    # Choix de la taille du "Bottom"
    with columns[1] :
        # Si l'utilisateur a choisi l'ensemble des équipes pour le "Top", alors le "Bottom" est vide
        if taille_groupes.loc["Top", "Taille"] == max_nb_team_saison :
            push_session_state("taille_bottom", max_nb_team_saison - taille_groupes.loc["Top", "Taille"])

        # Sinon, la taille maximale du "Bottom" est égale au nombre d'équipe maximum moins la taille du "Top"
        else :
            push_session_state("taille_bottom", min(max_nb_team_saison - taille_groupes.loc["Top", "Taille"],
                    get_session_state("taille_bottom")))
            load_session_state("taille_bottom")
            st.slider(taille_groupes.loc["Bottom", "Slider"], min_value = 0,
                    max_value = max_nb_team_saison - taille_groupes.loc["Top", "Taille"], **key_widg("taille_bottom"))
            
        taille_groupes.loc["Bottom", "Taille"] = get_session_state("taille_bottom")
    
    # Calcul de la taille du "Middle" en fonction des choix pour la taille du "Top" et du "Bottom"
    taille_groupes.loc["Middle", "Taille"] = max_nb_team_saison - taille_groupes.loc["Top", "Taille"] - taille_groupes.loc["Bottom", "Taille"]

    # Après avoir choisi la taille des groupes, l'utilisateur doit choisir le groupe a étudier parmi les groupes ayant une taille > 0
    # Dans le cas ou l'utilisateur a choisi la taille maximale pour le "Top", cela veut dire que les autres groupes sont vides, et il
    # n'est donc pas possible de choisir un groupe : le seul groupe possible est "Global", qui correspond à l'ensemble des équipes
    with columns[2] :
        # Variable booléenne pour savoir si il n'y a que le groupe "Global" qui est disponible
        global_seulement = taille_groupes.loc["Top", "Taille"] == max_nb_team_saison

        # On créé une liste qui contient tous les groupes sélectionnables (non vide)
        groupe_non_vide = taille_groupes[taille_groupes.Taille > 0].index.tolist()*(not(global_seulement)) + ["Global"]
        
        # Choix du groupe à étudier stocké dans la variable "groupe_select"
        if "groupe_select_zone_centre" in st.session_state and st.session_state["groupe_select_zone_centre"] not in groupe_non_vide :
            del st.session_state["groupe_select_zone_centre"]
        load_session_state("groupe_select")
        groupe_select = st.radio("Groupe à afficher", groupe_non_vide, horizontal = True, **key_widg("groupe_select"))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 7) b) Sélection des équipes à étudier dans le cas ou l'utilisateur à décider d'étudier une ou plusieurs équipes en particulier


else :  
    # Création d'une liste contenant l'ensemble des équipes présentes dans les données
    liste_equipes = zones_de_centre["Équipe"].unique()

    # Choix d'une ou plusieurs équipes à étudier, stockées dans la liste "equipes_select"
    filtre_session_state("équipe", liste_equipes)
    load_session_state("équipe")
    equipes_select = st.multiselect("Équipe à afficher", liste_equipes, **key_widg("équipe"))

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 8) Filtrage du dataframe selon les groupes/équipes choisis


# On fixe comme index du dataframe le couple ("Saison", "Équipe") dans le but de pouvoir filtrer facilement le dataframe en fonction
# du choix des groupes/équipes de l'utilisateur
zones_de_centre.set_index(["Saison", "Équipe"], inplace = True)

# Cas ou l'utilisateur à choisit d'étudier un groupe d'équipe

# Si l'utilisateur a choisi d'étudier l'ensemble des équipes ("Global"), alors il n'y a pas besoin de filtrer les équipes

# Pour pouvoir filtrer le dataframe "zones_de_centre" en fonction du groupe sélectionner, nous allons lui attribuer une nouvelle colonne
# "Groupe", qui, pour chaque ligne (chaque event), indiquera le groupe de l'équipe associée à cet event.

# Le groupe de chaque équipe varie en fonction des saisons, et pour connaitre le groupe de chaque équipe pour chaque saison, nous allons
# utilisé le dictionnaire "dico_classement_SB", qui stocke pour l'ensemble des saisons disponibles le classement de l'ensemble des
# compétitions disponibles (sous forme de liste, ou le premier élèment de la liste est la 1ère équipe au classement)
if choix_categorie == "Choisir Top/Middle/Bottom" and groupe_select != "Global" :
    for saison in choix_saisons :
        # On récupère sous forme de liste le classement du championnat pour la saison itérée
        classement_saison = dico_classement_SB[saison]

        # Récupération du "Top", dont la taille est égale au nombre d'équipes total moins la taille du "Middle" moins la taille du
        # "Bottom".
        # On n'utilise pas la commande "classement_saison[:taille_groupes.loc["Top", "Taille"]]" (qui est plus intuitive) pour gérer les
        # cas ou l'utilisateur a sélectionné plusieurs saisons ayant un nombre d'équipes différent.
        top_saison = classement_saison[:nb_team_saison[saison] - taille_groupes.loc["Middle", "Taille"] - taille_groupes.loc["Bottom", "Taille"]]

        # Récupération du "Middle"
        middle_saison = classement_saison[nb_team_saison[saison] - taille_groupes.loc["Middle", "Taille"] -
                        taille_groupes.loc["Bottom", "Taille"]:nb_team_saison[saison] - taille_groupes.loc["Bottom", "Taille"]]
        
        # Récupération du "Bottom"
        bottom_saison = classement_saison[nb_team_saison[saison] - taille_groupes.loc["Bottom", "Taille"]:]

        # Attribution des groupes à toutes les lignes du dataframe
        # on utilise l'outil "idx" qui est l'index slicer de Pandas, qui permet de filtrer les multi-index (lorsque l'index du dataframe
        # est composé de plusieurs colonnes)
        zones_de_centre.loc[idx[saison, top_saison], "Groupe"] = "Top"
        zones_de_centre.loc[idx[saison, middle_saison], "Groupe"] = "Middle"
        zones_de_centre.loc[idx[saison, bottom_saison], "Groupe"] = "Bottom"
        
        # Filtrage du dataframe pour ne garder que les events associés à des équipes appartenant au groupe sélectionné
        zones_de_centre = zones_de_centre[zones_de_centre.Groupe == groupe_select]
    
# Cas ou l'utilisateur a décidé d'étudier des équipes en particulier
elif (choix_categorie == "Choisir équipe") :
    # Filtrage du dataframe en ne gardant que les équipes sélectionnées
    zones_de_centre = zones_de_centre.loc[:, liste_equipes, :]

# Nous n'avons dorénavant plus besoin d'utiliser le couple ("Saison", "Équipe") comme index du dataframe, nous allons donc redéfinir
# ces variables en tant que colonne et mettre la variable "centre_id" comme index
zones_de_centre.set_index("centre_id", append = True, inplace = True)


# Nous créons maintenant un nouveau dataframe ne contenant que les events correspondant à des centres du dataframe "zones_de_centre"
centres = zones_de_centre[zones_de_centre.Centre == 1]

# On stop la suite du programme s'il n'y a pas de centre correspondant aux critères choisis par l'utilisateur
if len(centres) == 0 :
    st.stop()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 9) Filtre supplémentaire pour les centres et l'affichage des Heatmaps


columns = st.columns(2, vertical_alignment = "center", gap = "large")

with columns[0] :
    # a) Sélection des centres ayant amené à des buts
    load_session_state("choix_centre_but")
    choix_centre_but = st.checkbox(f"Filter les centres ayant amenés à un but (dans les {nb_events_suivant} évènements suivants le centre)",
                                   **key_widg("choix_centre_but"))
    
    # b) Choix d'afficher tous les centres du même coté sur la Heatmap de gauche
    load_session_state("choix_sym_gauche")
    if st.checkbox("Afficher tous les centres du même coté sur la Heatmap de gauche", **key_widg("choix_sym_gauche")) :
        # Dans le cas ou l'utilisateur a choisi la cette option, on effectue la symétrie des coordonnées des centres ayant été effectués
        # sur la moitié droite du terrain (quand leur position "y_loc" est > 40)
        centres.loc[centres.y_loc > 40, ["y_loc", "y_pass"]] = 80 - centres.loc[centres.y_loc > 40, ["y_loc", "y_pass"]]
    
    # c) Choix de la partie du corps utilisée pour le centre
    load_session_state("partie_du_corps")
    partie_du_corps = st.selectbox("Partie du corps utilisée pour centrer", ["Pied gauche", "Pied droit", "All"],
                    **key_widg("partie_du_corps"))

# Filtre du dataframe pour ne garder que les centres ayant amené à un but si l'utilisateur a sélectionné cette option
if choix_centre_but :
    centres = centres[centres.But == "Oui"]

# Filtre du dataframe pour ne garder que les centres ayant été effectué du pied droit si l'utilisateur a sélectionné cette option
if partie_du_corps == "Pied droit" :
    centres = centres[centres["Partie du corps"] == "Right Foot"]

# Filtre du dataframe pour ne garder que les centres ayant été effectué du pied gauche si l'utilisateur a sélectionné cette option
elif partie_du_corps == "Pied gauche" :
    centres = centres[centres["Partie du corps"] == "Left Foot"]

with columns[1] :
    # d) Choix de la façon de compter les centres pour l'affichage des Heatmaps (en pourcentage, en comptant le nombre total, etc)
    # On définit une liste "liste_type_compt" qui stocke tous les types de comptages possibles.
    # En fonction de si l'utilisateur a choisi l'option "choix_centre_but" ou non, l'utilisateur pourra afficher le pourcentage de
    # centre ayant amené à des buts pour chaque zone quadrillée de la Heatmap
    liste_type_compt = (["Pourcentage", "Pourcentage sans %", "Valeur", "Aucune valeur"] 
                        + (1 - choix_centre_but)*["Pourcentage de but"] + (1 - choix_centre_but)*["Pourcentage de but sans %"])
    
    # Choix de la façon de compter pour la Heatmap de gauche
    load_session_state("type_compt_gauche")
    type_compt_gauche = st.selectbox("Type de comptage Heatmap de gauche", liste_type_compt, **key_widg("type_compt_gauche"))
    
    # Choix de la façon de compter pour la Heatmap de droite
    load_session_state("type_compt_droite")
    type_compt_droite = st.selectbox("Type de comptage Heatmap de droite", liste_type_compt, **key_widg("type_compt_droite"))

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 10) Choix de la taille des deux Heatmaps (nombre de lignes et de colonnes pour quadriller les zones du terrain) et choix (ou non)
# d'une zone de la Heatmap à étudier en particulier


columns = st.columns(2, vertical_alignment = "center", gap = "large")

with columns[0] :
    columns2 = st.columns(2)

    with columns2[0] :
        # a) Choix du nombre de colonnes pour la Heatmap de gauche
        init_session_state("nb_col_gauche", 5)
        load_session_state("nb_col_gauche")
        nb_col_gauche = st.number_input("Nombre de colonnes pour la Heatmap de gauche", min_value = 1, step = 1,
                                **key_widg("nb_col_gauche"))

    with columns2[1] :
        # b) Choix du nombre de lignes pour la Heatmap de gauche     
        init_session_state("nb_lignes_gauche", 5)
        load_session_state("nb_lignes_gauche")
        nb_lignes_gauche = st.number_input("Nombre de ligne pour la Heatmap de gauche", min_value = 1, step = 1,
                **key_widg("nb_lignes_gauche"))
    
    # c) Choix de la colonne de la zone de la Heatmap de gauche à étudier en particulier (si l'utilisateur choisi 0, alors on garde les
    # centres de toutes les zones de la Heatmap de gauche)
    push_session_state("choix_col_gauche", min(nb_col_gauche, get_session_state("choix_col_gauche")))
    load_session_state("choix_col_gauche")
    choix_col_gauche = st.number_input("Choisir une colonne pour la Heatmap de gauche", min_value = 0, step = 1,
        max_value = nb_col_gauche, **key_widg("choix_col_gauche"))
    
    # d) Choix de la ligne de la zone de la Heatmap de gauche à étudier en particulier (si l'utilisateur choisi 0, alors on garde les
    # centres de toutes les zones de la Heatmap de gauche)
    push_session_state("choix_ligne_gauche", min(nb_lignes_gauche, get_session_state("choix_ligne_gauche")))
    load_session_state("choix_ligne_gauche")
    choix_ligne_gauche = st.number_input("Choisir une ligne pour la Heatmap de gauche", min_value = 0, step = 1,
        max_value = nb_lignes_gauche, **key_widg("choix_ligne_gauche"))

with columns[1] :
    columns2 = st.columns(2)

    with columns2[0] :
        # e) Choix du nombre de colonnes pour la Heatmap de droite
        init_session_state("nb_col_droite", 5)
        load_session_state("nb_col_droite")
        nb_col_droite = st.number_input("Nombre de colonnes pour la Heatmap de droite", min_value = 1, step = 1,
                **key_widg("nb_col_droite"))

    with columns2[1] :
        # f) Choix du nombre de lignes pour la Heatmap de droite     
        init_session_state("nb_lignes_droite", 5)
        load_session_state("nb_lignes_droite")
        nb_lignes_droite = st.number_input("Nombre de lignes pour la Heatmap de droite", min_value = 1, step = 1,
                **key_widg("nb_lignes_droite"))
        
st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Dans le cas ou une zone a été sélectionnée sur la Heatmap de gauche : filtre du dataframe des zones de réceptions de centre et
# possibilité de choisir une zone sur la Heatmap de droite pour laquelle afficher les positions de départ et d'arrivée des tirs.

df_recep_select = centres.copy()
df_shot_select = pd.DataFrame()

if (choix_ligne_gauche != 0) & (choix_col_gauche != 0) :

    df_recep_select = centres[(centres.x_loc >= (60 + (60/nb_lignes_gauche)*(choix_ligne_gauche - 1))) &
                    (centres.x_loc < (60 + (60/nb_lignes_gauche)*(choix_ligne_gauche))) &
                    (centres.y_loc >= (80/nb_col_gauche)*(choix_col_gauche - 1)) &
                    (centres.y_loc < (80/nb_col_gauche)*(choix_col_gauche))]
    
    with columns[1] :

        push_session_state("choix_col_droite", min(nb_col_droite, get_session_state("choix_col_droite")))
        load_session_state("choix_col_droite")
        choix_col_droite = st.number_input("Choisir une colonne pour la Heatmap de droite", min_value = 0, step = 1,
            max_value = nb_col_droite, **key_widg("choix_col_droite"))
        
        push_session_state("choix_ligne_droite", min(nb_lignes_droite, get_session_state("choix_ligne_droite")))
        load_session_state("choix_ligne_droite")
        choix_ligne_droite = st.number_input("Choisir une ligne pour la Heatmap de droite", min_value = 0, step = 1,
            max_value = nb_lignes_droite, **key_widg("choix_ligne_droite"))

    df_shot_select = df.loc[df_recep_select.index]
    df_shot_select = df_shot_select[df_shot_select.Tireur != ""]
    
    if choix_centre_but :
        df_shot_select = df_shot_select[df_shot_select.But == "Oui"]
    
    if (choix_ligne_droite != 0) & (choix_col_droite != 0) :
        df_shot_select = df_shot_select[(df_shot_select.x_loc >= (60 + (60/nb_lignes_droite)*(choix_ligne_droite - 1))) &
                        (df_shot_select.x_loc < (60 + (60/nb_lignes_droite)*(choix_ligne_droite))) &
                        (df_shot_select.y_loc >= (80/nb_col_droite)*(choix_col_droite - 1)) &
                        (df_shot_select.y_loc < (80/nb_col_droite)*(choix_col_droite))]

if len(df_recep_select) == 0 :
    type_compt_droite = "Aucune valeur"


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage du titre


choix_saisons = sorted(choix_saisons)

bool_taille_saison = (len(choix_saisons) > 1)
saison_title = []
saison_title.append(f'la saison {choix_saisons[0]}')
saison_title.append(f'les saisons {", ".join(choix_saisons[:-1])} et {choix_saisons[-1]}')

if choix_categorie == "Choisir Top/Middle/Bottom" :
    bool_taille_groupe = 0
    grp_title = [groupe_select]

else :
    bool_taille_groupe = (len(equipes_select) > 1)
    grp_title = [f'{equipes_select[0]}', f'{", ".join(equipes_select[:-1])} et {equipes_select[-1]}']

st.markdown(f"<p style='text-align: center;'>Heatmap {dico_label[choix_categorie][0]} {grp_title[bool_taille_groupe]} sur {saison_title[bool_taille_saison]}</p>",
                unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des heatmaps


fig_centre, fig_recep, ax_centre, ax_recep = heatmap_centre(centres, df_recep_select, nb_col_gauche, nb_lignes_gauche, nb_col_droite,
                                            nb_lignes_droite, type_compt_gauche, type_compt_droite, liste_type_compt)

if (choix_col_gauche != 0) & (choix_ligne_gauche != 0) :
    rect = patches.Rectangle(((80/nb_col_gauche)*(choix_col_gauche - 1), 60 + (60/nb_lignes_gauche)*(choix_ligne_gauche - 1)),
                                80/nb_col_gauche, 60/nb_lignes_gauche, linewidth=5, edgecolor='r', facecolor='r', alpha=0.6)
    ax_centre.add_patch(rect)

    if (choix_ligne_droite != 0) & (choix_col_droite != 0) :
        rect = patches.Rectangle(((80/nb_col_droite)*(choix_col_droite - 1), 60 + (60/nb_lignes_droite)*(choix_ligne_droite - 1)),
                                    80/nb_col_droite, 60/nb_lignes_droite, linewidth=5, edgecolor='r', facecolor='r', alpha=0.6)
        ax_recep.add_patch(rect)

columns = st.columns(2, vertical_alignment = "top", gap = "large")

with columns[0] :
    st.pyplot(fig_centre)

with columns[1] :
    st.pyplot(fig_recep)

st.markdown(f"<p style='text-align: center;'>Nombre total de centres : {len(centres)}</p>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des positions des tirs dans le cas ou une zone de réception a été sélectionnée


if len(df_shot_select) == 0 :
    st.stop()

st.divider()

columns = st.columns(2, vertical_alignment = "bottom", gap = "large")

with columns[0] :
    
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=1, pitch_color=None, line_color = "green", half = True,
            linewidth = 1.5, spot_scale = 0.002, goal_type = "box")

    fig_shot, ax_shot = pitch.draw(constrained_layout=True, tight_layout=False)

    ax_shot.set_ylim(min(df_shot_select.x_loc) - 5, 125)
    
    arrows_color = pd.Series("red", index = df_shot_select.index)
    arrows_color[df_shot_select.But == "Oui"] = "blue"

    pitch.arrows(df_shot_select.x_loc, df_shot_select.y_loc, df_shot_select.x_shot, df_shot_select.y_shot, color = arrows_color, ax = ax_shot,
                 width = 1)

    st.pyplot(fig_shot)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des positions des tirs dans la cage dans le cas ou une zone de réception a été sélectionnée


with columns[1] :
    fig_cage = plt.figure(figsize=(20,8))

    ax_cage = fig_cage.gca()
    ax_cage.set_axis_off()

    rapport_dim = 80/68

    width_poteaux = rapport_dim*0.12

    rayon_ballon = 0.11*rapport_dim

    x1=[36, 36, 44, 44, 44 + width_poteaux, 44 + width_poteaux, 36 - width_poteaux, 36 - width_poteaux]
    y1=[0, 2.67, 2.67, 0, 0, 2.67 + width_poteaux, 2.67 + width_poteaux, 0]
    
    plot_poteaux = patches.Polygon(np.array([x1, y1]).T, color = "black")
    ax_cage.add_patch(plot_poteaux)

    x_lim_min = 36 - rapport_dim
    x_lim_max = 44 + rapport_dim
    ax_cage.set_xlim(x_lim_min, x_lim_max)

    y_lim_min = -0.2
    y_lim_max = 2.67 + rapport_dim
    ax_cage.set_ylim(y_lim_min, y_lim_max)

    df_shot_select_cage = df_shot_select[(~df_shot_select.z_shot.isna()) & (df_shot_select.x_shot > 120 - rapport_dim) &
        (df_shot_select.y_shot > x_lim_min + rayon_ballon) & (df_shot_select.y_shot < x_lim_max - rayon_ballon)
        & (df_shot_select.z_shot < y_lim_max - rayon_ballon)]
    
    shot_color = pd.Series("red", index = df_shot_select_cage.index)
    shot_color[df_shot_select_cage.But == "Oui"] = "blue"

    ax_cage.scatter(df_shot_select_cage["y_shot"], df_shot_select_cage["z_shot"], s = 27**2, marker = "o", edgecolors = "black",
                    lw = 2, color = shot_color)

    st.pyplot(fig_cage)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des informations sur les tirs venant de la zone de centre sélectionnée dans le cas ou une équipe a été sélectionnée


if choix_categorie == "Choisir équipe" :

    st.divider()

    expander = st.expander("Tableau des tirs/buts pour la zone sélectionnée sur la Heatmap de gauche")

    with expander :        
        st.dataframe(df_shot_select[["Date", "Journée", "Domicile", "Extérieur", "Minute", "Centreur", "But", "Tireur", "Équipe"]],
                     hide_index = True)