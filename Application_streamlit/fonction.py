# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import numpy as np
import pandas as pd
import sqlite3
from mplsoccer import VerticalPitch

from variable import colormapred, path_effect_1, colormapblue, path_effect_2


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
# Définitions des fonctions génériques


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


def label_heatmap1(bin_statistic) :
    """Fonction qui permet de définir les paramètres d'affichage de la légende des heatmaps, en fonction du type de comptage choisi
    pour les zones de début d'action et les zones de tir
    Le dictionnaire contient comme clé les différents types de comptage, et comme valeur les statistiques à afficher et le format
    du texte de la légende des heatmaps

    Args:
        bin_statistic (_type_): Valeur contenu dans chaque zone/bin du terrain

    Returns:
        _type_: dictionnaire
    """

    dico_label_heatmap = {
        "Pourcentage" : {"statistique" : np.round(bin_statistic, 2), "str_format" : '{:.0%}'},
        "Pourcentage sans %" : {"statistique" : 100*np.round(bin_statistic, 2), "str_format" : '{:.0f}'},
        "Valeur" : {"statistique" : bin_statistic, "str_format" : '{:.0f}'},
    }
    return dico_label_heatmap


def label_heatmap2(bin_statistic, bin_statistic_but) :
    """Fonction qui permet de définir les paramètres d'affichage de la légende des heatmaps, en fonction du type de comptage choisi
    pour les zones de centre
    Le dictionnaire est une concaténation du dictionnaire pour les autres heatmaps, avec le rajout des types de comptage disponible
    pour les heatmaps de centre

    Args:
        bin_statistic (_type_): Valeur contenu dans chaque zone/bin du terrain
        bin_statistic_but (_type_): Valeur contenu dans chaque zone/bin du terrain pour les centres qui ont amenés à un but

    Returns:
        _type_: dictionnaire
    """
    dico_label_heatmap = label_heatmap1(bin_statistic)
    dico_label_heatmap.update({
        "Pourcentage de but" : {"statistique" : np.round(np.nan_to_num((bin_statistic_but/bin_statistic), 0), 2),
                                "str_format" : '{:.0%}'},
        "Pourcentage de but sans %" : {"statistique" : 100*np.round(np.nan_to_num((bin_statistic_but/bin_statistic), 0), 2),
                                       "str_format" : '{:.0f}'}
    })
    return dico_label_heatmap



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 1/ Zones de centre


@st.cache_data
def heatmap_centre(data_centre, data_recep, nb_col_gauche, nb_ligne_gauche, nb_col_droite, nb_ligne_droite, type_compt_gauche,
                   type_compt_droite, liste_type_compt) :
    """Fonction permettant la création des heatmaps des zones de centre et de réception des centres
    Définit dans un premier temps le terrain et les caractéristiques de la figure, puis affiche les statistiques des données
    passées en paramètre

    Args:
        data_centre (_type_): Dataframe contenant les informations sur les zones de départ de centre
        data_recep (_type_): Dataframe contenant les informations sur les zones de réception de centre
        nb_col_gauche (_type_): nombre de colonne de la heatmap de gauche
        nb_ligne_gauche (_type_): nombre de ligne de la heatmap de gauche
        nb_col_droite (_type_): nombre de colonne de la heatmap de droite
        nb_ligne_droite (_type_): nombre de ligne de la heatmap de droite
        type_compt_gauche (_type_): Type de comptage de la heatmap de gauche
        type_compt_droite (_type_): Type de comptage de la heatmap de droite
        liste_type_compt (_type_): Liste contenant tous les types de comptage possibles
    """

    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", half = True, axis = True,
                          label = True, tick = True, linewidth = 1.5, spot_scale = 0.002, goal_type = "box")
    
    fig_centre, ax_centre = pitch.draw(constrained_layout=True, tight_layout=False)

    ax_centre.spines[:].set_visible(False)

    fig_centre.set_facecolor("none")
    fig_centre.set_edgecolor("none")
    ax_centre.set_facecolor((1, 1, 1))

    ax_centre.set_xticks(np.arange(80/(2*nb_col_gauche), 80 - 80/(2*nb_col_gauche) + 1, 80/nb_col_gauche),
                labels = np.arange(1, nb_col_gauche + 1, dtype = int))
    ax_centre.set_yticks(np.arange(60 + 60/(2*nb_ligne_gauche), 120 - 60/(2*nb_ligne_gauche) + 1, 60/nb_ligne_gauche),
                labels = np.arange(1, nb_ligne_gauche + 1, dtype = int))
    ax_centre.tick_params(axis = "y", right = False, labelright = False)
    ax_centre.tick_params(axis = "x", top = False, labeltop = False)

    ax_centre.set_xlim(0, 80)
    ax_centre.set_ylim(60, 125)

    fig_recep, ax_recep = pitch.draw(constrained_layout=True, tight_layout=False)

    ax_recep.spines[:].set_visible(False)

    fig_recep.set_facecolor("none")
    fig_recep.set_edgecolor("none")
    ax_recep.set_facecolor((1, 1, 1))

    ax_recep.set_xticks(np.arange(80/(2*nb_col_droite), 80 - 80/(2*nb_col_droite) + 1, 80/nb_col_droite),
                        labels = np.arange(1, nb_col_droite + 1, dtype = int))
    ax_recep.set_yticks(np.arange(60 + 60/(2*nb_ligne_droite), 120 - 60/(2*nb_ligne_droite) + 1, 60/nb_ligne_droite),
                labels = np.arange(1, nb_ligne_droite + 1, dtype = int))
    ax_recep.tick_params(axis = "y", right = False, labelright = False)
    ax_recep.tick_params(axis = "x", top = False, labeltop = False)

    ax_recep.set_xlim(0, 80)
    ax_recep.set_ylim(60, 125)

    bin_statistic_centre = pitch.bin_statistic(data_centre.x_loc, data_centre.y_loc, statistic='count',
                        bins=(nb_ligne_gauche*2, nb_col_gauche), normalize = type_compt_gauche in liste_type_compt[:2])
    
    bin_statistic_recep = pitch.bin_statistic(data_recep.x_pass, data_recep.y_pass, statistic='count',
                        bins=(nb_ligne_droite*2, nb_col_droite), normalize = type_compt_droite in liste_type_compt[:2])

    if type_compt_gauche != "Aucune valeur" :
        bin_statistic_but_centre = pitch.bin_statistic(data_centre[data_centre.But == "Oui"].x_loc,
                            data_centre[data_centre.But == "Oui"].y_loc, statistic='count', bins=(nb_ligne_gauche*2, nb_col_gauche))
         
        dico_label_heatmap_centre = label_heatmap2(bin_statistic_centre["statistic"], bin_statistic_but_centre["statistic"])[type_compt_gauche]

        bin_statistic_centre["statistic"] = dico_label_heatmap_centre["statistique"]

        str_format_centre = dico_label_heatmap_centre["str_format"]

        pitch.label_heatmap(bin_statistic_centre, exclude_zeros = True, fontsize = int(100/(nb_col_gauche + nb_ligne_gauche)) + 2,
            color='#f4edf0', ax = ax_centre, ha='center', va='center', str_format=str_format_centre, path_effects=path_effect_2)
        
    if type_compt_droite != "Aucune valeur" :
        bin_statistic_but_recep = pitch.bin_statistic(data_recep[data_recep.But == "Oui"].x_pass,
                            data_recep[data_recep.But == "Oui"].y_pass, statistic='count', bins=(nb_ligne_droite*2, nb_col_droite))
        
        dico_label_heatmap_recep = label_heatmap2(bin_statistic_recep["statistic"], bin_statistic_but_recep["statistic"])[type_compt_droite]

        bin_statistic_recep["statistic"] = dico_label_heatmap_recep["statistique"]

        str_format_recep = dico_label_heatmap_recep["str_format"]

        pitch.label_heatmap(bin_statistic_recep, exclude_zeros = True, fontsize = int(100/(nb_col_droite + nb_ligne_droite)) + 2,
            color='#f4edf0', ax = ax_recep, ha='center', va='center', str_format=str_format_recep, path_effects=path_effect_2)
        
    pitch.heatmap(bin_statistic_centre, ax = ax_centre, cmap = colormapred, edgecolor='#000000', linewidth = 0.2)

    pitch.heatmap(bin_statistic_recep, ax = ax_recep, cmap = colormapblue, edgecolor='#000000', linewidth = 0.2)
        
    return(fig_centre, fig_recep, ax_centre, ax_recep)