"""Fakes e fábricas compartilhadas pelos testes"""

from conversor.modelo import Aula, Bloco, Slide


def fabricar_bloco(
    texto: str,
    x: float = 0.1,
    y: float = 0.1,
    tamanho: float = 10.0,
    cor: int = 0,
    fonte: str = "CMR10",
) -> Bloco:
    """Cria um ``Bloco`` com altura fixa de 0.02 a partir do canto (x, y)

    Exemplo: ``fabricar_bloco("Provas", x=0.24, y=0.16, fonte="CMBX10")``

    :param texto: conteúdo do span
    :param x: borda esquerda, em proporção da largura
    :param y: topo, em proporção da altura
    :param tamanho: tamanho da fonte em pontos
    :param cor: cor RGB (``0xFFFFFF`` = branco)
    :param fonte: nome da fonte, como o PyMuPDF informa
    :return: ``Bloco`` pronto para os testes
    """
    return Bloco(
        texto=texto,
        tamanho=tamanho,
        bbox=(x, y, x + 0.05, y + 0.02),
        cor=cor,
        negrito=False,
        fonte=fonte,
    )


class ExtratorFalso:
    """Substitui ``extrair``: devolve uma aula de 1 slide sem abrir PDF e registra as chamadas"""

    def __init__(self) -> None:
        self.chamadas: list[tuple[str, str]] = []

    def __call__(self, pdf_caminho: str, grupo: str) -> Aula:
        """Registra a chamada e devolve a aula fixa, como ``extrair`` devolveria

        Exemplo: ``ExtratorFalso()("pdf/x.pdf", "bruno_gslides").slides[0].pagina`` → ``1``

        :param pdf_caminho: caminho que o pipeline pediu para ler
        :param grupo: grupo classificado
        :return: aula de 1 slide com o bloco ``"Olá"``
        """
        self.chamadas.append((pdf_caminho, grupo))
        slide = Slide(pdf=pdf_caminho, pagina=1, blocos=[fabricar_bloco("Olá")])
        return Aula(
            id="04",
            titulo="Conectividade",
            grupo=grupo,
            pdf=pdf_caminho,
            slides=[slide],
        )
