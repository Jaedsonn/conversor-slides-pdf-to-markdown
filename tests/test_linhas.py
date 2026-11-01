from conversor.linhas import agrupar_linhas, juntar_linhas, texto_da_linha
from tests.fakes import fabricar_bloco


def test_agrupar_linhas_junta_mesma_altura_e_ordena_por_x() -> None:
    largura = fabricar_bloco("Largura", x=0.6, y=0.044)
    busca = fabricar_bloco("Busca", x=0.52, y=0.044)
    abaixo = fabricar_bloco("Profundidade", x=0.52, y=0.068)

    linhas = agrupar_linhas([abaixo, largura, busca])

    assert [[bloco.texto for bloco in linha] for linha in linhas] == [
        ["Busca", "Largura"],
        ["Profundidade"],
    ]


def test_agrupar_linhas_tolera_pequena_diferenca_de_altura() -> None:
    # Regressão Cid p.60: "NP" (CMSY10) fica 0.001 acima das palavras CMBX10
    linhas = agrupar_linhas(
        [fabricar_bloco("de", y=0.161), fabricar_bloco("NP", x=0.2, y=0.160)]
    )
    assert len(linhas) == 1


def test_agrupar_linhas_vazio() -> None:
    assert agrupar_linhas([]) == []


def test_texto_da_linha_tira_espacos_das_pontas() -> None:
    linha = [fabricar_bloco("O problema "), fabricar_bloco(" das")]
    assert texto_da_linha(linha) == "O problema das"


def test_juntar_linhas_usa_separador_entre_linhas() -> None:
    blocos = [fabricar_bloco("b", y=0.5), fabricar_bloco("a", y=0.1)]
    assert juntar_linhas(blocos) == "a b"
    assert juntar_linhas(blocos, separador="\n") == "a\nb"
