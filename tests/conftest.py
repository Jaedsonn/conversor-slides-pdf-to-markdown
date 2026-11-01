"""Configuração comum: os testes de integração usam caminhos relativos à raiz"""

from pathlib import Path

import pytest

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def rodar_na_raiz_do_projeto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(RAIZ_DO_PROJETO)
