from pathlib import Path

from conversor.escrever import (
    nome_do_markdown,
    renderizar_markdown,
    salvar_markdown,
    slugificar,
)
from conversor.modelo import Aula, Slide
from tests.fakes import fabricar_bloco


def _aula_de_exemplo() -> Aula:
    com_titulo = Slide(
        pdf="pdf/teoria/04 - Conectividade.pdf",
        pagina=1,
        titulo="Caminhos",
        blocos=[fabricar_bloco("Um", y=0.5), fabricar_bloco("passeio", x=0.3, y=0.5)],
    )
    sem_titulo = Slide(pdf="pdf/teoria/04 - Conectividade.pdf", pagina=2)
    return Aula(
        id="04",
        titulo="Conectividade",
        grupo="bruno_gslides",
        pdf="pdf/teoria/04 - Conectividade.pdf",
        slides=[com_titulo, sem_titulo],
    )


def test_slugificar_remove_acentos_e_simbolos() -> None:
    assert slugificar("17c NP-Completude(2)") == "17c-np-completude-2"
    assert slugificar("06 Árvores") == "06-arvores"
    assert slugificar("12 Ordenação Topológica") == "12-ordenacao-topologica"


def test_nome_do_markdown_usa_id_e_titulo() -> None:
    assert (
        nome_do_markdown(Aula("16A", "Algoritmos", "hamilton_beamer"))
        == "16a-algoritmos.md"
    )


def test_renderizar_markdown_monta_cabecalho_e_slides() -> None:
    esperado = (
        "# 04 — Conectividade\n\n"
        "> Fonte: `pdf/teoria/04 - Conectividade.pdf` · grupo: `bruno_gslides`\n\n"
        "## Caminhos (slide 1)\n\n"
        "Um passeio\n\n"
        "## Slide 2 (slide 2)\n"
    )
    assert renderizar_markdown(_aula_de_exemplo()) == esperado


def test_salvar_markdown_grava_em_nn_slug(tmp_path: Path) -> None:
    destino = salvar_markdown(_aula_de_exemplo(), tmp_path / "md")
    assert destino == tmp_path / "md" / "04-conectividade.md"
    assert destino.read_text(encoding="utf-8").startswith("# 04 — Conectividade")
