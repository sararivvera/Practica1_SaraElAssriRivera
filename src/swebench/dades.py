"""Càrrega i validació de les dues taules de puntuacions que utilitza la interfície."""
import pandas as pd

from .configuracio import DADES_PROCESSADES

def carregar_dades():
    original = pd.read_csv(DADES_PROCESSADES / 'puntuacions_processades.csv')
    oficial = pd.read_csv(DADES_PROCESSADES / 'resultats_oficials_processats.csv')
    camps = {'model','modalitat','puntuacio_pct','configuracio','font_valor'}
    for df, mida in [(original,4),(oficial,7)]:
        if not camps.issubset(df.columns) or len(df) != mida:
            raise ValueError('Arxiu de puntuacions incomplet: executa python preprocessament.py')
        if not df['puntuacio_pct'].between(0,100).all() or not df['configuracio'].is_unique:
            raise ValueError('Puntuacions fora de rang o configuracions duplicades')
    if original['puntuacio_pct'].round(1).tolist() != [74.9,69.1,52.8,30.8]:
        raise ValueError('La reproducció de les quatre puntuacions ha canviat')
    if oficial['puntuacio_pct'].round(1).tolist() != [74.9,71.0,69.1,68.1,54.7,54.6,23.6]:
        raise ValueError('La taula oficial no coincideix amb la font de 2025')
    return original, oficial

