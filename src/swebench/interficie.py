"""Interfície Streamlit. Les figures i la càrrega de dades tenen mòduls propis."""
import streamlit as st

from .configuracio import PRINCIPAL, AMPLIADA, PLOT_CONFIG
from .dades import carregar_dades
from .grafics import (format_num, format_signe, grafica_general, grafica_parella)


@st.cache_data(show_spinner=False)
def _carregar_dades_cache():
    return carregar_dades()


def executar():
    st.set_page_config(page_title='SWE-bench Verified: redisseny', page_icon='📊', layout='wide')
    original, oficial = _carregar_dades_cache()
    st.title('SWE-bench Verified: redisseny')
    st.caption('Comparació de rendiment en tasques d’enginyeria de software - Dades publicades el 7 d’agost de 2025')

    vista = st.radio(
        'Dades que vols explorar',
        [PRINCIPAL, AMPLIADA],
        horizontal=True,
        help='La primera vista corregeix exactament la gràfica errònia. La segona amplia el context amb la taula oficial de set models.',
    )
    ampliat = vista == AMPLIADA
    dades = (oficial if ampliat else original).sort_values('puntuacio_pct',ascending=False).copy()

    if ampliat:
        st.caption('**Ampliació documental.** Set puntuacions de la taula oficial de SWE-bench Verified (2025). No són la mateixa selecció de la diapositiva errònia.')
    else:
        st.caption('**Correcció de la diapositiva original.** Quatre puntuacions independents: les dues variants de GPT-5 no són segments acumulables.')

    st.subheader('1. Comparació proporcional')
    st.plotly_chart(grafica_general(dades, ampliat),use_container_width=True,config=PLOT_CONFIG)
    st.caption('Totes les barres parteixen de **0** i comparteixen l’escala **0–100 %**. Els valors exactes són visibles al costat de cada barra; els colors estan explicats a la llegenda.')

    st.subheader('2. Compara dues puntuacions')
    llista = dades['configuracio'].tolist()
    esquerra,dreta = st.columns(2)
    with esquerra:
        a = st.selectbox('A - configuració a comparar',llista, index=0,key='seleccio_a_'+str(ampliat))
    with dreta:
        possibles_b = [x for x in llista if x != a]
        predeterminada = ('OpenAI o3 - raonament alt' if ampliat else 'OpenAI o3 - amb raonament')
        b = st.selectbox(
            'B - configuració de referència',possibles_b,
            index=possibles_b.index(predeterminada) if predeterminada in possibles_b else 0,
            key='seleccio_b_'+str(ampliat),
        )
    indexats = dades.set_index('configuracio')
    pa = float(indexats.at[a,'puntuacio_pct'])
    pb = float(indexats.at[b,'puntuacio_pct'])
    ma = str(indexats.at[a,'modalitat']); mb = str(indexats.at[b,'modalitat'])
    diferencia = pa-pb
    relativa = 100*diferencia/pb
    idx = 100*pa/pb
    m1,m2,m3 = st.columns(3)
    m1.metric('Diferència A − B',format_signe(diferencia)+' pp')
    m2.metric('Variació relativa respecte de B',format_signe(relativa,2)+' %')
    m3.metric('Índex A (B = 100)',format_num(idx,2))

    if ma != mb:
        st.warning('Les etiquetes d’esforç de raonament són diferents. La comparació és descriptiva i no permet atribuir la diferència només al raonament.')
    else:
        st.info('Les etiquetes d’esforç coincideixen, però això no garanteix condicions d’avaluació completament idèntiques.')

    metrica = st.radio('Representació de la parella', ['Puntuació (%)','Índex normalitzat (B = 100)'], horizontal=True)
    amb_index = metrica.startswith('Índex')
    st.plotly_chart(grafica_parella(a,b,pa,pb,ma,mb,amb_index,ampliat),use_container_width=True,config=PLOT_CONFIG)
    if amb_index:
        st.caption('**Índex relatiu (no és un percentatge d’encerts).** B = 100; A = 100 × puntuació(A) / puntuació(B). Les barres parteixen de zero.')
    else:
        st.caption('**Puntuació:** percentatge de tasques resoltes (0–100). Diferència A − B en punts percentuals.')

    # Dada real d'eficiència reportada només per a la parella que es va comparar
    models_parella = {str(indexats.at[a,'model']),str(indexats.at[b,'model'])}
    if models_parella == {'GPT-5','OpenAI o3'} and ma == mb and ma in {'Amb raonament','Raonament alt'}:
        st.info('**Informació addicional d’eficiència (OpenAI, 2025):** en la comparació GPT-5 vs. o3 amb raonament alt, OpenAI declara un **22 % menys de tokens de sortida** i un **45 % menys de crides a eines** per a GPT-5. No són punts de SWE-bench i, per això, no es barregen al mateix gràfic.')

    with st.expander('Metodologia, fonts i limitacions'):
        st.markdown('''
**Què mesura SWE-bench Verified?** La proporció de tasques de programació resoltes en un conjunt verificat de casos reals.

**Abast de l'avaluació (2025).** El conjunt original conté 500 tasques. OpenAI documenta que els seus resultats es calculen amb **477**, després d'excloure 23 casos que no s'executaven de manera fiable a la seva infraestructura. Les 500 metadades no contenen els encerts individuals dels models i no permeten reconstruir les puntuacions publicades.

**Comparabilitat.** Les puntuacions s'han transcrit de fonts d'OpenAI publicades en la mateixa data. A la taula ampliada, `high` indica esforç de raonament alt; quan l'esforç no s'hi especifica, no l'hem etiquetat arbitràriament com a absència de raonament.

**Límit temporal.** Són resultats del llançament de 2025, no un rànquing actual. El febrer de 2026, OpenAI va assenyalar problemes de contaminació del benchmark que limiten la interpretació de comparacions actuals.

**Fonts:** [Presentació original](https://www.youtube.com/watch?v=0Uu_VJeVVfo&t=300s) - [OpenAI: GPT-5 per a desenvolupadors](https://openai.com/index/introducing-gpt-5-for-developers/) - [SWE-bench Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) - [Nota metodològica del 2026](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)
''')

    st.caption('Elaboració pròpia - URV - P1 de Modelització i Visualització de Dades. Les puntuacions mantenen la font i la data originals.')
