# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import numpy as np
import pandas as pd
import sqlite3
from mplsoccer import VerticalPitch

from variables import colormapred, path_effect_1, colormapblue, path_effect_2


# ---------------------------------------------- Précision fonctionnement session state --------------------------------------------------------------------------------------
"""J'ai mit en place des session states pour chaque page de l'application, qui sont
indépendants au niveau des pages. Cela permets de garder ses choix de widget lorsqu'on switch de page, ou lorsque sur une page
on modifie la valeur d'un widget et que par conséquent, en l'absence de session state, cela peut réinitialiser le choix
de certains widgets de cette même page
Les clés des éléments du session state de chaque pages on toujours pour suffixe le 'nom' de la page, pour les différencier de 
page en page. Par exemple, le widget "nt_top" est initialisé une seule fois à 3 pour chaque page, et donc les éléments
"nb_top_zone_centre", "nb_top_evo_saison"... seront tous initialisé à 3
De plus, au début des codes de chaque page, je transforme les fonctions modifiant le session state en fonction partielle avec
la fixation du paramètre "suffixe" avec le nom de la page en question
Cela permets de ne pas avoir à définir le paramètre "suffixe" à chaque appel de ces fonctions, mais aussi de pouvoir "standardiser"
les appels de fonctions entre certaines pages, car la clé de session state passée en argument de chaque fonction sera la clé
globale qui ne contient pas le suffixe de la page
Cette clé globale correspond au paramètre "key_init" de ces fonctions"""


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Définition des fonctions génériques


def load_session_state(key_init, suffixe) :
    """Associe à la clé d'un widget la valeur de l'élément du session state correspondante
    La clé du widget est toujours égale à "widg_" + la clé de l'élément du session_state
    Dans un premier temps, on regarde le cas ou l'élément du session state spécifique à la page n'a pas encore été défini, mais
    qu'il possède bien une valeur par défaut dans le session state. Ex : l'élément "nb_top" n'a pas encore été défini pour la 1ère
    page (donc l'élément "nb_top_met_disc") mais l'élément "nb_top" est initialisé par défaut à 3 dans le programme Main. L'élément
    "nb_top_met_disc" sera donc initialisé à 3. A l'inverse, pour la page heatmap zone de début d'action par exemple, l'élément
    "équipe" n'est pas initialisé par défaut dans le programme Main, la fonction n'associera donc pas de valeur par défaut
    à l'élément "équipe_deb_action"
    L'association est réalisée dans l'unique cas ou la valeur de l'élément du session state a été initialisée

    Args:
        key_init (_type_): Clé globale de l'élément du session state, sans le suffixe correspondant à la page en question
        suffixe (_type_): Suffixe correspondant à la page (ex : deb_action)
    """

    key = key_init + suffixe

    if key not in st.session_state and key_init in st.session_state :
        st.session_state[key] = st.session_state[key_init]

    if key in st.session_state :
        st.session_state["widg_" + key] = st.session_state[key]


def store_session_state(key) :
    """Modifie la valeur d'un élément du session state en le remplaçant par la sélection du widget en question
    La clé du widget est toujours égale à "widg_" + la clé de l'élément du session_state
    Args:
        key : Clé du widget
    """
    st.session_state[key] = st.session_state["widg_" + key]


def key_widg(key_init, suffixe) :
    """Renvoie les paramètres génériques des fonctions "widgets" de Streamlit, permettant de ne pas avoir à écrire les paramètres
    à chaque appel, mais aussi de stantardiser ces appels car sur les codes de chaque page, on appelle une fonction partielle
    de key_widg, ou le suffixe est fixé en début de code, et le seule paramètre à écrire est donc "key_init", qui est le même entre
    chaque page
    Pour faire simple, lorsqu'on appel des fonctions widgets, au lieu d'écrire les paramètre "key", "on_change" et "args", on a
    juste appeler la fonction key_widg avec comme paramètre la clé globale du widget dans cette fonction widget

    Args:
        key_init (_type_): Clé globale de l'élément du session state, sans le suffixe correspondant à la page en question
        suffixe (_type_): Suffixe correspondant à la page (ex : deb_action)

    Returns:
        _type_: paramètres de la fonction widget
    """
    key = key_init + suffixe
    return {"key" : "widg_" + key, "on_change" : store_session_state, "args" : [key]}


def get_session_state(key_init, suffixe) :
    """Retourne la valeur de l'élément du session state voulue
    Permets de retourner la valeur de l'élément générique du session state (s'il existe) dans le cas ou l'élément du session state
    spécifique à la page n'a pas encore été initialisé

    Args:
        key_init (_type_): Clé globale de l'élément du session state, sans le suffixe correspondant à la page en question
        suffixe (_type_): Suffixe correspondant à la page (ex : deb_action)

    Returns:
        _type_: Valeur du session state correspondant à la clé passé en paramètre
    """
    key = key_init + suffixe
    if key in st.session_state :
        return st.session_state[key]
    elif key_init in st.session_state :
        return st.session_state[key_init]
    

def push_session_state(key_init, value, suffixe) :
    """Modifie la valeur d'un élément du session state

    Args:
        key_init (_type_): Clé globale de l'élément du session state, sans le suffixe correspondant à la page en question
        value (_type_): Valeur à modifier
        suffixe (_type_): Suffixe correspondant à la page (ex : deb_action)
    """
    key = key_init + suffixe
    st.session_state[key] = value


def init_session_state(key_init, value, suffixe) :
    """Initialise une valeur pour un élément du session state s'il n'est pas encore défini

    Args:
        key_init (_type_): Clé globale de l'élément du session state, sans le suffixe correspondant à la page en question
        value (_type_): Valeur à initialiser
        suffixe (_type_): Suffixe correspondant à la page (ex : deb_action)
    """

    key = key_init + suffixe
    if key not in st.session_state :
        st.session_state[key] = value

    
def filtre_session_state(key_init, liste, suffixe) :
    """Permet de vérifier que les valeurs d'une liste du session state soient bien comprises dans les valeurs disponible avec le
    widget associé

    Args:
        key_init (_type_): Clé globale de l'élément du session state, sans le suffixe correspondant à la page en question
        liste (_type_): liste qui doit inclure le session state
        suffixe (_type_): Suffixe correspondant à la page (ex : deb_action)
    """

    key = key_init + suffixe
    if key in st.session_state :
        st.session_state[key] = [i for i in st.session_state[key] if i in liste]


@st.cache_data
def execute_SQL(_cursor, stat, params) :
    """Éxécute une requête sql via un curseur et des paramètres

    Args:
        cursor : Curseur lié à la base de donnée
        stat : Requête à effectuer
        params : Paramètres de la requête

    Returns:
        _type_: Résultat de la requête
    """

    req = _cursor.execute(stat, params)
    return req.fetchall(), req.description

def dico_texte_comptage(statistiques_zones, statistiques_but_zones) :
    """Fonction qui permet de définir les paramètres d'affichage de la légende des heatmaps, en fonction du type de comptage choisi
    pour les zones de début d'action et les zones de tir
    Le dictionnaire contient comme clé les différents types de comptage, et comme valeur les statistiques à afficher et le format
    du texte de la légende des heatmaps

    Args:
        statistiques_zones (_type_): Valeur contenu dans chaque zone/bin du terrain

    Returns:
        _type_: dictionnaire
    """

    dico_texte_comptage = {
        "Pourcentage" : {"statistique" : np.round(statistiques_zones, 2), "str_format" : '{:.0%}'},
        "Pourcentage sans %" : {"statistique" : 100*np.round(statistiques_zones, 2), "str_format" : '{:.0f}'},
        "Valeur" : {"statistique" : statistiques_zones, "str_format" : '{:.0f}'},
        "Pourcentage de but" : {"statistique" : np.round(np.nan_to_num((statistiques_but_zones/statistiques_zones), 0), 2),
                                "str_format" : '{:.0%}'},
        "Pourcentage de but sans %" : {"statistique" : 100*np.round(np.nan_to_num((statistiques_but_zones/statistiques_zones), 0), 2),
                                       "str_format" : '{:.0f}'}
    }
    return dico_texte_comptage


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 1/ Zones de centre


# Fonction permettant de créer la Heatmap pour les zones de centres (Heatmap de gauche)
@st.cache_data
def heatmap_zones_de_centre(centres, nb_colonnes, nb_lignes, type_comptage, liste_type_compt) :
    # Création du terrain vertical mpl_soccer
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", half = True, axis = True,
                          label = True, tick = True, linewidth = 1.5, spot_scale = 0.002, goal_type = "box")
    
    # On dessine le terrain avec la fonction "pitch.draw", qui retourne une figure et un axe Matplotlib
    figure_pitch, axe_pitch = pitch.draw(constrained_layout=True, tight_layout=False)

    # On enlève les lignes inutiles autour du terrain
    axe_pitch.spines[:].set_visible(False)

    figure_pitch.set_facecolor("none")
    figure_pitch.set_edgecolor("none")
    axe_pitch.set_facecolor((1, 1, 1))

    # Affichage des "ticks" des colonnes, c'est à dire leur numéro de 1 à "nb_colonnes"
    axe_pitch.set_xticks(np.arange(80/(2*nb_colonnes), 80 - 80/(2*nb_colonnes) + 1, 80/nb_colonnes),
                labels = np.arange(1, nb_colonnes + 1, dtype = int))
    
    # Suppression des "ticks" des colonnes en haut du terrain, on affiche le numéro des colonnes en bas
    axe_pitch.tick_params(axis = "x", top = False, labeltop = False)
    
    # Affichage des "ticks" des lignes, c'est à dire leur numéro de 1 à "nb_lignes"
    axe_pitch.set_yticks(np.arange(60 + 60/(2*nb_lignes), 120 - 60/(2*nb_lignes) + 1, 60/nb_lignes),
                labels = np.arange(1, nb_lignes + 1, dtype = int))
    
    # Suppression des "ticks" des lignes à droite du terrain, on affiche le numéro des lignes à gauche
    axe_pitch.tick_params(axis = "y", right = False, labelright = False)
    
    # Délimitation du terrain : on garde toute la largeur, cependant on n'affiche que la deuxième moitié, correspondant à la moitié
    # ou les équipes attaquent (d'après Stats Bomb)
    axe_pitch.set_xlim(0, 80)
    axe_pitch.set_ylim(60, 125)

    # Calcul des statistiques des différentes zones de la Heatmap : on compte pour chaque zone le nombre de centres qui ont été
    # effectués à l'intérieur.
    # Le paramètre normalize permet de normaliser le comptage de chaque zone, c'est à dire calculer le pourcentage des centres présents
    # dans cette zone par rapport au nombre total de centre
    # On normalise donc le comptage si l'utilisateur a choisi le type de comptage "Pourcentage" ou "Pourcentage sans %" pour la Heatmap
    # de gauche
    statistiques_zones = pitch.bin_statistic(centres.x_loc, centres.y_loc, statistic='count',
                        bins=(nb_lignes*2, nb_colonnes), normalize = type_comptage in liste_type_compt[:2])

    # Affichage du texte associé au statistiques des différentes zones, dans le cas ou l'utilisateur a bien choisi d'afficher ces stats
    if type_comptage != "Aucune valeur" :
        # On récupère les statistiques liées aux centres ayant amenés à un but
        statistiques_but_zones = pitch.bin_statistic(centres[centres.But == "Oui"].x_loc,
                            centres[centres.But == "Oui"].y_loc, statistic='count', bins=(nb_lignes*2, nb_colonnes))
        
        # On récupère via la fonction "texte_stat_heatmap" (implémentée ci-dessus) les valeurs des statistiques ainsi que le format
        # du texte à afficher pour ces stats
        dico_texte_stat_heatmap = dico_texte_comptage(statistiques_zones["statistic"], statistiques_but_zones["statistic"])

        # On récupère le dictionnaire correspondant au type de comptage choisi par l'utilisateur
        texte_stat_heatmap = dico_texte_stat_heatmap[type_comptage]

        # On modifie les statistiques actuelles après les avoir adaptées pour le type de comptage choisi
        statistiques_zones["statistic"] = texte_stat_heatmap["statistique"]

        # Format du texte a afficher pour le comptage
        format_texte_stat = texte_stat_heatmap["str_format"]

        # Ajout du texte lié aux statistiques des zones à la Heatmap
        pitch.label_heatmap(statistiques_zones, exclude_zeros = True, fontsize = int(100/(nb_colonnes + nb_lignes)) + 2,
            color='#f4edf0', ax = axe_pitch, ha='center', va='center', str_format=format_texte_stat, path_effects=path_effect_2)
        
    # Assignation de la Heatmap au terrain
    pitch.heatmap(statistiques_zones, ax = axe_pitch, cmap = colormapred, edgecolor='#000000', linewidth = 0.2)
        
    return(figure_pitch, axe_pitch)


# Fonction permettant de créer la Heatmap pour les zones de réception des centres (Heatmap de droite)
@st.cache_data
def heatmap_zones_de_recep(recep_centres, nb_colonnes, nb_lignes, type_comptage, liste_type_compt) :
    # Création du terrain vertical mpl_soccer
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", half = True, axis = True,
                          label = True, tick = True, linewidth = 1.5, spot_scale = 0.002, goal_type = "box")
    
    # On dessine le terrain avec la fonction "pitch.draw", qui retourne une figure et un axe Matplotlib
    figure_pitch, axe_pitch = pitch.draw(constrained_layout=True, tight_layout=False)

    # On enlève les lignes inutiles autour du terrain
    axe_pitch.spines[:].set_visible(False)

    figure_pitch.set_facecolor("none")
    figure_pitch.set_edgecolor("none")
    axe_pitch.set_facecolor((1, 1, 1))

    # Affichage des "ticks" des colonnes, c'est à dire leur numéro de 1 à "nb_colonnes"
    axe_pitch.set_xticks(np.arange(80/(2*nb_colonnes), 80 - 80/(2*nb_colonnes) + 1, 80/nb_colonnes),
                labels = np.arange(1, nb_colonnes + 1, dtype = int))
    
    # Suppression des "ticks" des colonnes en haut du terrain, on affiche le numéro des colonnes en bas
    axe_pitch.tick_params(axis = "x", top = False, labeltop = False)
    
    # Affichage des "ticks" des lignes, c'est à dire leur numéro de 1 à "nb_lignes"
    axe_pitch.set_yticks(np.arange(60 + 60/(2*nb_lignes), 120 - 60/(2*nb_lignes) + 1, 60/nb_lignes),
                labels = np.arange(1, nb_lignes + 1, dtype = int))
    
    # Suppression des "ticks" des lignes à droite du terrain, on affiche le numéro des lignes à gauche
    axe_pitch.tick_params(axis = "y", right = False, labelright = False)
    
    # Délimitation du terrain : on garde toute la largeur, cependant on n'affiche que la deuxième moitié, correspondant à la moitié
    # ou les équipes attaquent (d'après Stats Bomb)
    axe_pitch.set_xlim(0, 80)
    axe_pitch.set_ylim(60, 125)

    # Calcul des statistiques des différentes zones de la Heatmap : on compte pour chaque zone le nombre de centres qui ont été
    # réceptionnés à l'intérieur.
    # Le paramètre normalize permet de normaliser le comptage de chaque zone, c'est à dire calculer le pourcentage des centres
    # réceptionnés dans cette zone par rapport au nombre total de centre
    # On normalise donc le comptage si l'utilisateur a choisi le type de comptage "Pourcentage" ou "Pourcentage sans %" pour la Heatmap
    # de droite
    statistiques_zones = pitch.bin_statistic(recep_centres.x_pass, recep_centres.y_pass, statistic='count',
                        bins=(nb_lignes*2, nb_colonnes), normalize = type_comptage in liste_type_compt[:2])

    # Affichage du texte associé au statistiques des différentes zones, dans le cas ou l'utilisateur a bien choisi d'afficher ces stats
    if type_comptage != "Aucune valeur" :
        # On récupère les statistiques liées aux centres ayant amenés à un but
        statistiques_but_zones = pitch.bin_statistic(recep_centres[recep_centres.But == "Oui"].x_pass,
                            recep_centres[recep_centres.But == "Oui"].y_pass, statistic='count', bins=(nb_lignes*2, nb_colonnes))
        
        # On récupère via la fonction "texte_stat_heatmap" (implémentée ci-dessus) les valeurs des statistiques ainsi que le format
        # du texte à afficher pour ces stats
        dico_texte_stat_heatmap = dico_texte_comptage(statistiques_zones["statistic"], statistiques_but_zones["statistic"])

        # On récupère le dictionnaire correspondant au type de comptage choisi par l'utilisateur
        texte_stat_heatmap = dico_texte_stat_heatmap[type_comptage]

        # On modifie les statistiques actuelles après les avoir adaptées pour le type de comptage choisi
        statistiques_zones["statistic"] = texte_stat_heatmap["statistique"]

        # Format du texte a afficher pour le comptage
        format_texte_stat = texte_stat_heatmap["str_format"]

        # Ajout du texte lié aux statistiques des zones à la Heatmap
        pitch.label_heatmap(statistiques_zones, exclude_zeros = True, fontsize = int(100/(nb_colonnes + nb_lignes)) + 2,
            color='#f4edf0', ax = axe_pitch, ha='center', va='center', str_format=format_texte_stat, path_effects=path_effect_2)
        
    # Assignation de la Heatmap au terrain
    pitch.heatmap(statistiques_zones, ax = axe_pitch, cmap = colormapblue, edgecolor='#000000', linewidth = 0.2)
        
    return(figure_pitch, axe_pitch)