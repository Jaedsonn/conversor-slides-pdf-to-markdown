import json
import unicodedata
from pathlib import Path

import pytest

from conversor.classificar import carregar_mapa_arquivos, classificar
from conversor.pipeline import listar_pdfs
from tests.conftest import RAIZ_DO_PROJETO

GRUPOS_JSON = RAIZ_DO_PROJETO / "grupos.json"
PASTA_PDF = RAIZ_DO_PROJETO / "pdf"


@pytest.fixture(scope="module")
def mapa() -> dict[str, str]:
    return carregar_mapa_arquivos(GRUPOS_JSON)


@pytest.mark.parametrize("arquivo", listar_pdfs(PASTA_PDF))
def test_todo_pdf_do_repositorio_tem_grupo(arquivo: str, mapa: dict[str, str]) -> None:
    assert classificar(arquivo, mapa) in {
        "bruno_gslides",
        "hamilton_beamer",
        "cid_latex",
        "notas_manuscritas",
    }


def test_classificar_aceita_nome_decomposto_nfd(mapa: dict[str, str]) -> None:
    nfd = unicodedata.normalize("NFD", "teoria/06 - Árvores.pdf")
    assert classificar(nfd, mapa) == "bruno_gslides"


def test_classificar_pdf_desconhecido_falha_com_nome(mapa: dict[str, str]) -> None:
    with pytest.raises(ValueError, match="99 - Falso.pdf"):
        classificar("teoria/99 - Falso.pdf", mapa)


def test_carregar_mapa_sem_secao_arquivos_falha(tmp_path: Path) -> None:
    config = tmp_path / "grupos.json"
    config.write_text(json.dumps({"grupos": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="arquivos"):
        carregar_mapa_arquivos(config)
