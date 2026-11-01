from conversor.estrategias.base import Estrategia
from conversor.linhas import agrupar_linhas, juntar_linhas, texto_da_linha
from conversor.modelo import Bloco, Slide

FAIXA_TITULO_BRUNO = 0.3
FAIXA_BARRA_HAMILTON = 0.1
COR_ITEM_ATUAL_HAMILTON = 0xFFFFFF
METADE_DA_PAGINA = 0.5
SEPARADOR_SECAO = " > "
FAIXA_TITULO_CID = 0.25
MARCADOR_ITEM_CID = "▷"


def _blocos_acima_de(slide: Slide, faixa: float) -> list[Bloco]:
    return [bloco for bloco in slide.blocos if bloco.bbox[1] < faixa]


class Bruno(Estrategia):
    """Google Slides: título = spans de maior fonte no topo, juntando todas as linhas"""

    def achar_titulo(self, slide: Slide) -> str:
        """Junta as linhas de maior fonte acima de ``FAIXA_TITULO_BRUNO``

        Exemplo: ``Bruno().achar_titulo(slide_p5)`` → ``"O problema das sete pontes de Königsberg ..."``

        :param slide: slide com blocos crus (antes da limpeza)
        :return: título, ou ``""`` se não houver texto no topo
        """
        topo = _blocos_acima_de(slide, FAIXA_TITULO_BRUNO)
        if not topo:
            return ""
        maior = max(bloco.tamanho for bloco in topo)
        return juntar_linhas([bloco for bloco in topo if bloco.tamanho == maior])


class Hamilton(Estrategia):
    """Beamer: título = itens brancos da barra (seção à esquerda, subseção à direita)"""

    def achar_titulo(self, slide: Slide) -> str:
        """Monta ``"Seção > Subseção"`` com os itens destacados da barra de navegação

        Exemplo: ``Hamilton().achar_titulo(slide_p10)`` → ``"M´etodos de Busca > Busca em Largura"``

        :param slide: slide com blocos crus; a barra ainda não pode ter sido removida
        :return: título, ou ``""`` se nenhum item estiver destacado
        """
        barra = [bloco for bloco in slide.blocos if _eh_item_atual_da_barra(bloco)]
        # Separa as metades ANTES de agrupar em linhas, seção e subseção podem
        # estar na mesma altura e não podem virar uma linha só
        esquerda = [bloco for bloco in barra if bloco.bbox[0] < METADE_DA_PAGINA]
        direita = [bloco for bloco in barra if bloco.bbox[0] >= METADE_DA_PAGINA]
        partes = (juntar_linhas(esquerda), juntar_linhas(direita))
        return SEPARADOR_SECAO.join(parte for parte in partes if parte)


def _eh_item_atual_da_barra(bloco: Bloco) -> bool:
    return bloco.bbox[1] < FAIXA_BARRA_HAMILTON and bloco.cor == COR_ITEM_ATUAL_HAMILTON


class Cid(Estrategia):
    """LaTeX: título = primeira linha do topo que começa em negrito (CMBX) e não é item ▷"""

    def achar_titulo(self, slide: Slide) -> str:
        """Devolve a primeira linha do topo que começa em fonte ``CMBX``

        Exemplo: ``Cid().achar_titulo(slide_p60)`` → ``"Provas de NP -completude: CV (cont.)"``

        :param slide: slide com blocos crus e bbox já sem rotação
        :return: título, ou ``""`` se o slide não tiver título (ex.: p.5)
        """
        linhas = agrupar_linhas(_blocos_acima_de(slide, FAIXA_TITULO_CID))
        titulos = (
            texto_da_linha(linha) for linha in linhas if _eh_linha_de_titulo(linha)
        )
        return next(titulos, "")


def _eh_linha_de_titulo(linha: list[Bloco]) -> bool:
    # Tudo no Cid tem 20,7 pt; só a fonte distingue o título. Itens em negrito
    # ("▷ Esquema:") começam pelo marcador, que vem em outra fonte (MSAM10)
    primeiro = linha[0]
    return "CMBX" in primeiro.fonte and not primeiro.texto.startswith(MARCADOR_ITEM_CID)


class Notas(Estrategia):
    """Notas manuscritas do iPad: não há texto extraível; transcrição fica para a T18"""

    def achar_titulo(self, slide: Slide) -> str:
        """Sempre vazio até a transcrição com visão (T18)

        Exemplo: ``Notas().achar_titulo(slide)`` → ``""``

        :param slide: slide sem blocos de texto
        :return: ``""``
        """
        return ""
