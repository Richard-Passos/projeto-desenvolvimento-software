"""Ponto de entrada da UI prototípica.

Uso recomendado a partir da raiz do projeto:

    $env:PYTHONPATH = "src"
    python -m ui.executar_ui

Também é possível executar o arquivo diretamente:

    python src/ui/executar_ui.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def _configurar_caminho_direto() -> None:
    """Permite executar este arquivo sem configurar PYTHONPATH manualmente."""
    if __package__:
        return
    raiz_src = Path(__file__).resolve().parents[1]
    caminho = str(raiz_src)
    if caminho not in sys.path:
        sys.path.insert(0, caminho)


def main() -> None:
    _configurar_caminho_direto()

    from ui.prototipo_pygame import main as iniciar_prototipo

    iniciar_prototipo()


if __name__ == "__main__":
    main()
