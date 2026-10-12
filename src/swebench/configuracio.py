"""Paràmetres visuals i rutes absolutes derivades de la ubicació del projecte."""
from pathlib import Path

ARREL_PROJECTE = Path(__file__).resolve().parents[2]
DADES_ORIGINALS = ARREL_PROJECTE / 'dades' / 'originals'
DADES_PROCESSADES = ARREL_PROJECTE / 'dades' / 'processades'

PRINCIPAL = 'Diapositiva original (4 configuracions)'
AMPLIADA = 'Taula oficial ampliada (7 models)'
COLOR_RAONAMENT = '#2DD4BF'
COLOR_ALTRE = '#A78BFA'
FONS = '#FFFFFF'
TEXT = '#0F172A'
TEXT_S = '#475569'
PLOT_CONFIG = {'displayModeBar': False, 'responsive': True}
