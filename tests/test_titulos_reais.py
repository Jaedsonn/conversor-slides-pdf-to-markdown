"""Integração: títulos de páginas reais, um caso por bug corrigido (lê PDFs de pdf/)"""

from functools import cache

import pytest

from conversor.estrategias import ESTRATEGIAS, estrategia_para
from conversor.extrair import extrair
from conversor.modelo import Aula

CONECTIVIDADE = ("pdf/teoria/04 - Conectividade.pdf", "bruno_gslides")
BFS = ("pdf/algoritmos/11a - BFS-DFS-Kosaraju-Tarjan.pdf", "hamilton_beamer")
ALGORITMOS = ("pdf/algoritmos/16A - Algoritmos.pdf", "hamilton_beamer")
NP_COMPLETUDE = ("pdf/algoritmos/17b - NP-Completude.pdf", "cid_latex")


@cache
def _aula_processada(pdf: str, grupo: str) -> Aula:
    # Cache: cada PDF é lido uma vez por sessão de teste, mantendo a suíte rápida
    return estrategia_para(grupo, ESTRATEGIAS).processar(extrair(pdf, grupo))


def _titulo(pdf_e_grupo: tuple[str, str], pagina: int) -> str:
    return _aula_processada(*pdf_e_grupo).slides[pagina - 1].titulo


def test_bruno_titulo_em_tres_linhas() -> None:
    titulo = _titulo(CONECTIVIDADE, 5)
    assert "O problema das sete pontes" in titulo
    assert titulo.count("Königsberg") == 2


@pytest.mark.parametrize(
    ("pdf_e_grupo", "pagina", "esperado"),
    [
        (CONECTIVIDADE, 20, "Terminologia de caminhamentos"),
        (BFS, 10, "M´etodos de Busca > Busca em Largura"),
        (ALGORITMOS, 8, "Algoritmo > Deﬁni¸c˜ao"),
        (NP_COMPLETUDE, 60, "Provas de NP -completude: CV (cont.)"),
        (NP_COMPLETUDE, 5, ""),
    ],
)
def test_titulos_reais(
    pdf_e_grupo: tuple[str, str], pagina: int, esperado: str
) -> None:
    assert _titulo(pdf_e_grupo, pagina) == esperado
