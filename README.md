# SWE-bench Verified - redisseny crític

**Pràctica 1 de Modelització i Visualització de Dades (URV) - Sara El Assri Rivera.**

Aplicació interactiva que redissenya el gràfic de la presentació de GPT-5 del 7 d’agost de 2025. La vista inicial conserva les quatre puntuacions de la diapositiva; la vista ampliada compara set resultats publicats a la taula oficial. Les diferències són descriptives i no impliquen causalitat.

## Estructura

```text
.
├── app.py                         # Entrada de Streamlit
├── src/
│   └── swebench/
│       ├── configuracio.py         # Rutes del projecte, colors i etiquetes
│       ├── dades.py                # Lectura i validació dels CSV processats
│       ├── grafics.py              # Gràfics Plotly i formats numèrics
│       ├── interficie.py           # Controls i pàgines de Streamlit
│       └── preprocessament.py      # Transformacions, filtratges i comparacions
├── dades/
│   ├── originals/                 # Valors transcrits i 500 tasques amb estat
│   └── processades/               # Taules preparades per a l'aplicació
├── .streamlit/config.toml         # Tema clar de la interfície
├── requirements.txt               # Dependències
└── .gitignore
```

La carpeta `dades/originals/` conté `puntuacions_diapositiva.csv`, `resultats_oficials_2025.csv` i `benchmark_500_amb_estat.csv`. La carpeta `dades/processades/` conté `puntuacions_processades.csv`, `resultats_oficials_processats.csv`, `benchmark_477.csv` i, després de processar, les taules auxiliars. **Les rutes són relatives a la ubicació del projecte, no al directori de treball del terminal.**

## Execució

Requereix **Python 3.10 o superior**. Des de l'arrel del repositori:

```bash
python -m pip install -r requirements.txt
python -m src.swebench.preprocessament
python -m streamlit run app.py
```

`src/swebench/preprocessament.py` comprova les 500 tasques i les 23 exclusions, calcula les sis comparacions possibles i regenera les taules de dades processades. Per tornar a descarregar les tasques oficials (opcional i amb connexió), instal·la `datasets` i executa:

```bash
python -m pip install datasets
python -m src.swebench.preprocessament --tornar-a-descarregar
```

**Nota metodològica:** les 500 metadades de SWE-bench Verified no inclouen els encerts individuals de cada model; les puntuacions de rendiment s'han transcrit de les publicacions d'OpenAI.

## Fonts

- [Presentació original d'OpenAI (07/08/2025)](https://www.youtube.com/watch?v=0Uu_VJeVVfo&t=300s)
- [Resultats de GPT-5 per a desenvolupadors (2025)](https://openai.com/index/introducing-gpt-5-for-developers/)
- [SWE-bench Verified (dataset)](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified)

La memòria acadèmica es lliura separadament.
