import pytest

from conversor.estrategias import ESTRATEGIAS, estrategia_para
from conversor.estrategias.achar_titulo import Bruno, Cid, Hamilton, Notas
from conversor.modelo import Aula, Bloco, Slide
from tests.fakes import fabricar_bloco

BRANCO = 0xFFFFFF
CINZA = 0x7F807F


def _slide(*blocos: Bloco) -> Slide:
    return Slide(pdf="x.pdf", pagina=1, blocos=list(blocos))


def test_estrategia_para_grupo_desconhecido_lista_os_validos() -> None:
    with pytest.raises(ValueError, match=r"'inexistente'.*cid_latex"):
        estrategia_para("inexistente", ESTRATEGIAS)


def test_estrategia_para_usa_o_registro_injetado() -> None:
    notas = Notas()
    assert estrategia_para("qualquer", {"qualquer": notas}) is notas


def test_limpar_padrao_devolve_a_mesma_aula() -> None:
    aula = Aula("15", "notas", "notas_manuscritas")
    assert Notas().limpar(aula) is aula


def test_registro_cobre_os_quatro_grupos() -> None:
    assert set(ESTRATEGIAS) == {
        "bruno_gslides",
        "hamilton_beamer",
        "cid_latex",
        "notas_manuscritas",
    }


def test_processar_preenche_titulo_de_cada_slide() -> None:
    aula = Aula(
        "15",
        "notas",
        "notas_manuscritas",
        slides=[Slide(pdf="x.pdf", pagina=1, titulo="velho")],
    )
    assert Notas().processar(aula).slides[0].titulo == ""


def test_bruno_junta_linhas_da_maior_fonte_e_ignora_fora_da_faixa() -> None:
    slide = _slide(
        fabricar_bloco("O problema", y=0.08, tamanho=21.6),
        fabricar_bloco("de Königsberg", y=0.21, tamanho=21.6),
        fabricar_bloco("Tipo", y=0.23, tamanho=16.0),
        fabricar_bloco("Rodapé gigante", y=0.95, tamanho=30.0),
    )
    assert Bruno().achar_titulo(slide) == "O problema de Königsberg"


def test_bruno_sem_texto_no_topo() -> None:
    assert Bruno().achar_titulo(_slide()) == ""


def test_hamilton_separa_secao_e_subsecao_na_mesma_altura() -> None:
    slide = _slide(
        fabricar_bloco("Algoritmo", x=0.40, y=0.007, cor=BRANCO),
        fabricar_bloco("Definição", x=0.52, y=0.007, cor=BRANCO),
        fabricar_bloco("Corretude", x=0.52, y=0.032, cor=CINZA),
    )
    assert Hamilton().achar_titulo(slide) == "Algoritmo > Definição"


def test_cid_ignora_item_em_negrito_com_marcador() -> None:
    slide = _slide(
        fabricar_bloco("▷", x=0.11, y=0.157, fonte="MSAM10"),
        fabricar_bloco("Esquema", x=0.14, y=0.155, fonte="CMBX10"),
    )
    assert Cid().achar_titulo(slide) == ""


def test_cid_pega_linha_inteira_que_comeca_em_cmbx() -> None:
    slide = _slide(
        fabricar_bloco("NP", x=0.05, y=0.03, fonte="CMSY8"),
        fabricar_bloco("Provas", x=0.24, y=0.161, fonte="CMBX10"),
        fabricar_bloco("NP", x=0.38, y=0.160, fonte="CMSY10"),
    )
    assert Cid().achar_titulo(slide) == "Provas NP"
