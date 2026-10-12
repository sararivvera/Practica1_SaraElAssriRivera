"""Reproducció del preprocessament de SWE-bench Verified.

Conserva les puntuacions comunicades per OpenAI separades de les metadades
oficials de les tasques. Cap metadata permet reconstruir encerts per model.
"""
from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path

import pandas as pd

from .configuracio import DADES_ORIGINALS, DADES_PROCESSADES

# Permet provar el preprocessament sobre una còpia de les dades, sense tocar originals.
def directoris(arrel_personalitzada: Path | None) -> tuple[Path, Path]:
    if arrel_personalitzada is None:
        originals, processades = DADES_ORIGINALS, DADES_PROCESSADES
    else:
        base = Path(arrel_personalitzada)
        originals = base / 'originals'
        processades = base / 'processades'
    processades.mkdir(parents=True, exist_ok=True)
    return originals, processades

EXCLOSOS = frozenset('''

astropy__astropy-7606
astropy__astropy-8707
astropy__astropy-8872
django__django-10097
django__django-7530
matplotlib__matplotlib-20488
matplotlib__matplotlib-20676
matplotlib__matplotlib-20826
matplotlib__matplotlib-23299
matplotlib__matplotlib-24970
matplotlib__matplotlib-25479
matplotlib__matplotlib-26342
psf__requests-6028
pylint-dev__pylint-6528
pylint-dev__pylint-7080
pylint-dev__pylint-7277
pytest-dev__pytest-5262
pytest-dev__pytest-7521
scikit-learn__scikit-learn-12973
sphinx-doc__sphinx-10466
sphinx-doc__sphinx-7462
sphinx-doc__sphinx-8265
sphinx-doc__sphinx-9367
'''.split())
assert len(EXCLOSOS) == 23

def preparar_puntuacions(directori: Path | None = None):
    """Validació, reestructuració i sis parelles úniques (sense duplicar A/B)."""
    originals, processades = directoris(directori)
    puntuacions = pd.read_csv(originals / 'puntuacions_diapositiva.csv')
    requisits = {'model', 'modalitat', 'puntuacio_pct', 'font_valor'}
    assert requisits.issubset(puntuacions.columns)
    for camp in ('model', 'modalitat', 'font_valor'):
        puntuacions[camp] = puntuacions[camp].astype('string').str.strip()
    puntuacions['puntuacio_pct'] = pd.to_numeric(puntuacions['puntuacio_pct'], errors='raise')
    assert len(puntuacions) == 4
    assert puntuacions['puntuacio_pct'].between(0, 100).all()
    assert puntuacions[list(requisits)].notna().all().all()
    assert not puntuacions[['model', 'modalitat']].duplicated().any()
    assert set(puntuacions['modalitat']) == {'Amb raonament', 'Sense raonament'}
    puntuacions['configuracio'] = puntuacions['model'] + ' - ' + puntuacions['modalitat'].str.lower()
    assert puntuacions['configuracio'].is_unique

    # Reconfiguració: files separades per model i modalitat, no barres apilades
    puntuacions = puntuacions.sort_values('puntuacio_pct', ascending=False).reset_index(drop=True)
    puntuacions['ordre_global'] = puntuacions.index + 1
    puntuacions.to_csv(processades / 'puntuacions_processades.csv', index=False, float_format='%.4f')

    # Exactament combinacions(4, 2) = 6. A és, convencionalment, la puntuació més alta
    files = []
    for ia, ib in combinations(range(len(puntuacions)), 2):
        a = puntuacions.iloc[ia]
        b = puntuacions.iloc[ib]
        diferencia = float(a['puntuacio_pct'] - b['puntuacio_pct'])
        relativa = diferencia / float(b['puntuacio_pct']) * 100
        mateixa = bool(a['modalitat'] == b['modalitat'])
        files.append({
            'configuracio_a': a['configuracio'], 'model_a': a['model'],
            'modalitat_a': a['modalitat'], 'puntuacio_a_pct': a['puntuacio_pct'],
            'configuracio_b': b['configuracio'], 'model_b': b['model'],
            'modalitat_b': b['modalitat'], 'puntuacio_b_pct': b['puntuacio_pct'],
            'diferencia_pp': diferencia,
            'variacio_relativa_pct_respecte_b': relativa,
            'index_a_base_b_100': float(a['puntuacio_pct']) / float(b['puntuacio_pct']) * 100,
            'mateixa_modalitat': mateixa,
            'advertiment': ('Modalitats diferents: comparació descriptiva, no causal.'
                           if not mateixa else
                           'Mateixa modalitat; les condicions tècniques poden variar.'),
        })
    comparacions = pd.DataFrame(files)
    assert len(comparacions) == 6
    assert (comparacions['diferencia_pp'] > 0).all()
    comparacions.to_csv(processades / 'comparacions_totes.csv', index=False, float_format='%.4f')
    return puntuacions, comparacions



def preparar_puntuacions_oficials(directori: Path | None = None):
    """Reconstrueix la taula addicional publicada per OpenAI el 07/08/2025.

    No barreja la diapositiva original amb dades d'altres fonts.
    """
    originals, processades = directoris(directori)
    dades = pd.read_csv(originals / 'resultats_oficials_2025.csv')
    camps = {'model', 'modalitat', 'puntuacio_pct', 'font_valor'}
    assert camps.issubset(dades.columns)
    assert len(dades) == 7
    for camp in ('model', 'modalitat', 'font_valor'):
        dades[camp] = dades[camp].astype('string').str.strip()
    dades['puntuacio_pct'] = pd.to_numeric(dades['puntuacio_pct'], errors='raise')
    assert dades[list(camps)].notna().all().all()
    assert dades['puntuacio_pct'].between(0,100).all()
    assert dades['model'].is_unique
    assert set(dades['modalitat']) == {'Raonament alt', 'Esforç no indicat'}
    # No s'infereix que els models sense etiqueta "high" funcionin sense raonament.
    dades['configuracio'] = dades['model'] + ' - ' + dades['modalitat'].str.lower()
    dades = dades.sort_values('puntuacio_pct', ascending=False).reset_index(drop=True)
    dades['ordre_global'] = dades.index + 1
    dades.to_csv(processades / 'resultats_oficials_processats.csv', index=False, float_format='%.4f')
    return dades



def comparar_configuracions(puntuacions: pd.DataFrame, configuracio_a: str, configuracio_b: str):
    """Comparació ORIENTADA d'A respecte de B, incloent resultats negatius."""
    if configuracio_a == configuracio_b:
        raise ValueError('Cal seleccionar dues configuracions diferents.')
    index = puntuacions.set_index('configuracio', verify_integrity=True)
    a = index.loc[configuracio_a]
    b = index.loc[configuracio_b]
    p_a, p_b = float(a['puntuacio_pct']), float(b['puntuacio_pct'])
    if p_b == 0:
        raise ValueError('No es pot normalitzar respecte d’una base zero.')
    return {
        'diferencia_pp': p_a - p_b,
        'variacio_relativa_pct': (p_a - p_b) / p_b * 100,
        'index_base_100': p_a / p_b * 100,
        'mateixa_modalitat': bool(a['modalitat'] == b['modalitat']),
    }



def comprovar_benchmark_local(directori: Path | None = None):
    """Verifica els CSV oficials ja descarregats sense requerir d'internet."""
    originals, processades = directoris(directori)
    meta = pd.read_csv(originals / 'benchmark_500_amb_estat.csv')
    casos = pd.read_csv(processades / 'benchmark_477.csv')
    assert len(meta) == 500 and len(casos) == 477
    assert meta['instance_id'].is_unique and casos['instance_id'].is_unique
    assert meta[['instance_id', 'repo', 'difficulty']].notna().all().all()
    assert casos[['instance_id', 'repo', 'difficulty']].notna().all().all()
    assert meta['inclosa_avaluacio_openai'].sum() == 477
    assert (~meta['inclosa_avaluacio_openai']).sum() == 23
    assert set(meta.loc[~meta['inclosa_avaluacio_openai'], 'instance_id']) == EXCLOSOS
    assert set(meta.loc[meta['inclosa_avaluacio_openai'], 'instance_id']) == set(casos['instance_id'])

    agrupat = (casos.groupby(['repo', 'difficulty'], dropna=False)
               .size().rename('n_tasques').reset_index())
    agrupat['pct_sobre_477'] = agrupat['n_tasques'] / len(casos) * 100
    agrupat['pct_dins_repo'] = (agrupat['n_tasques'] /
        agrupat.groupby('repo')['n_tasques'].transform('sum') * 100)
    agrupat = agrupat.sort_values(['repo', 'n_tasques'], ascending=[True, False])
    assert agrupat['n_tasques'].sum() == 477
    agrupat.to_csv(processades / 'distribucio_repo_dificultat.csv', index=False, float_format='%.4f')
    return meta, casos, agrupat



def descarregar_benchmark(directori: Path | None = None):
    """Opcional: torna a obtenir les 500 tasques si no hi ha CSV locals."""
    originals, processades = directoris(directori)
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError('Cal instal-lar datasets: pip install datasets') from exc
    original = load_dataset('SWE-bench/SWE-bench_Verified', split='test').to_pandas()
    assert len(original) == 500
    assert {'instance_id', 'repo', 'difficulty'}.issubset(original.columns)
    meta = original[['instance_id', 'repo', 'difficulty']].copy()
    assert set(EXCLOSOS).issubset(set(meta['instance_id']))
    meta['inclosa_avaluacio_openai'] = ~meta['instance_id'].isin(EXCLOSOS)
    meta.to_csv(originals / 'benchmark_500_amb_estat.csv', index=False)
    meta.loc[meta['inclosa_avaluacio_openai']].to_csv(processades / 'benchmark_477.csv', index=False)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tornar-a-descarregar', action='store_true',
                        help='Torna a baixar les 500 tasques des de Hugging Face')
    args = parser.parse_args()
    if args.tornar_a_descarregar:
        descarregar_benchmark()
    puntuacions, comparacions = preparar_puntuacions()
    oficials = preparar_puntuacions_oficials()
    meta, casos, grups = comprovar_benchmark_local()
    print(f'Validació: {len(meta)} tasques, {len(casos)} incloses, {len(grups)} grups.')
    print(f'Puntuacions: {len(puntuacions)} configuracions; {len(comparacions)} parelles úniques.')
    print(f'Ampliació oficial del 2025: {len(oficials)} models, mateixa prova SWE-bench Verified.')
    print(comparacions[['configuracio_a', 'configuracio_b', 'diferencia_pp',
                        'variacio_relativa_pct_respecte_b', 'mateixa_modalitat']].to_string(index=False))


if __name__ == '__main__':
    main()
