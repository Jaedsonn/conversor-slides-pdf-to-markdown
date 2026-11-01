"""Agrupamento de spans (palavras) em linhas visuais, compartilhado por todos os grupos"""

from conversor.modelo import Bloco

# Em proporção da altura da página. A menor distância entre linhas observada é
# ~0.025 (barra de navegação do Hamilton, 6 pt); 0.01 separa linhas sem quebrar
# spans de uma mesma linha, que têm o mesmo y
TOLERANCIA_LINHA = 0.01


def _centro_vertical(bloco: Bloco) -> float:
    return (bloco.bbox[1] + bloco.bbox[3]) / 2


def agrupar_linhas(
    blocos: list[Bloco], tolerancia: float = TOLERANCIA_LINHA
) -> list[list[Bloco]]:
    """Agrupa spans pela altura (centro vertical) e ordena cada linha da esquerda p/ direita

    O PyMuPDF entrega palavras soltas em alguns grupos (Hamilton, Cid); juntar por
    linha é o que permite montar títulos e parágrafos legíveis

    Exemplo: ``agrupar_linhas([busca, em, largura])`` → ``[[busca, em, largura]]``

    :param blocos: spans de uma página, em qualquer ordem
    :param tolerancia: diferença máxima de centro vertical para ficar na mesma linha
    :return: linhas de cima para baixo, cada uma com spans ordenados por x
    """
    linhas: list[list[Bloco]] = []
    for bloco in sorted(blocos, key=_centro_vertical):
        ancora = linhas[-1][0] if linhas else None
        if (
            ancora
            and abs(_centro_vertical(bloco) - _centro_vertical(ancora)) <= tolerancia
        ):
            linhas[-1].append(bloco)
            continue
        linhas.append([bloco])
    return [sorted(linha, key=lambda bloco: bloco.bbox[0]) for linha in linhas]


def texto_da_linha(linha: list[Bloco]) -> str:
    """Junta os spans de uma linha com um espaço, descartando espaços das pontas

    Exemplo: ``texto_da_linha([Bloco("Busca ", ...), Bloco("em", ...)])`` → ``"Busca em"``

    :param linha: spans já ordenados por x (saída de ``agrupar_linhas``)
    :return: texto da linha
    """
    return " ".join(bloco.texto.strip() for bloco in linha if bloco.texto.strip())


def juntar_linhas(blocos: list[Bloco], separador: str = " ") -> str:
    """Agrupa os spans em linhas e junta o texto delas com ``separador``

    Exemplo: ``juntar_linhas(spans_do_titulo)`` → ``"O problema das sete pontes de Königsberg"``

    :param blocos: spans em qualquer ordem
    :param separador: texto colocado entre linhas (``" "`` para títulos, ``"\\n"`` para corpo)
    :return: texto de todas as linhas, de cima para baixo
    """
    return separador.join(texto_da_linha(linha) for linha in agrupar_linhas(blocos))
