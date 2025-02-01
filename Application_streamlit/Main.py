import streamlit as st

dico_session_state = {
    "taille_top" : 3,
    "taille_bottom" : 3,
    'type_action' : ["Open play"],
    "partie_corps" : "All",
    "choix_col_gauche" : 0,
    "choix_ligne_gauche" : 0,
    "choix_col_droite" : 0,
    "choix_ligne_droite" : 0    
}

for key in dico_session_state.keys() :
    if key not in st.session_state :
        st.session_state[key] = dico_session_state[key]

liste_pages_app = []
liste_pages_app.append(st.Page("pages/10_zones_de_centre.py", title = "Zones de centre"))

navigation_app = st.navigation({
    "Applications" : liste_pages_app
})

navigation_app.run()