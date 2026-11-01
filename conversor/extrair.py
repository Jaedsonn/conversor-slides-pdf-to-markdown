"""Único módulo que conhece o PyMuPDF: traduz o PDF para o modelo do projeto"""

import re
from pathlib import Path
from typing import TypedDict

import pymupdf

from conversor.modelo import Aula, Bloco, Slide

PADRAO_NOME_PDF = re.compile(r"(\w+)\s*-\s*(.+)")


class SpanPymupdf(TypedDict):
    """Subconjunto das chaves de um span de ``page.get_text("dict")`` que usamos"""

    text: str
    bbox: tuple[float, float, float, float]
    size: float
    font: str
    flags: int
    color: int


def ler_identificacao(pdf_caminho: str) -> tuple[str, str]:
    """Separa o id e o título da aula a partir do nome do arquivo

    Exemplo: ``ler_identificacao("pdf/teoria/04 - Conectividade.pdf")`` → ``("04", "Conectividade")``

    :param pdf_caminho: caminho (ou nome) do PDF no formato ``"<id> - <titulo>.pdf"``
    :return: tupla ``(id, titulo)``
    :raises ValueError: se o nome não seguir o padrão
    """
    nome = Path(pdf_caminho).stem
    encontrado = PADRAO_NOME_PDF.match(nome)
    if encontrado is None:
        raise ValueError(
            f"Nome de PDF fora do padrão: {nome!r}. "
            "Esperado '<id> - <titulo>.pdf', ex.: '04 - Conectividade.pdf'."
        )
    return encontrado.group(1), encontrado.group(2)


def extrair(pdf_caminho: str, grupo: str) -> Aula:
    """Copia fielmente o PDF para o modelo. Não limpa nem interpreta

    Exemplo: ``extrair("pdf/teoria/04 - Conectividade.pdf", "bruno_gslides")``

    :param pdf_caminho: caminho do PDF a ler
    :param grupo: grupo de estilo do PDF (ver ``grupos.json``)
    :return: ``Aula`` com um ``Slide`` por página, ainda sem título
    """
    id_aula, titulo = ler_identificacao(pdf_caminho)
    aula = Aula(id=id_aula, titulo=titulo, grupo=grupo, pdf=pdf_caminho)
    with pymupdf.open(pdf_caminho) as documento:
        for numero, page in enumerate(documento, start=1):
            aula.slides.append(_extrair_pagina(page, pdf_caminho, numero))
    return aula


def _extrair_pagina(page: pymupdf.Page, pdf_caminho: str, numero: int) -> Slide:
    # rotation_matrix leva o bbox para o referencial visual: o 17b (Cid) tem
    # rotation=270 e sem isso y=0 não seria o topo da página
    matriz, largura, altura = page.rotation_matrix, page.rect.width, page.rect.height
    slide = Slide(pdf=pdf_caminho, pagina=numero)
    slide.blocos = [
        span_para_bloco(span, matriz, largura, altura) for span in _spans_de_texto(page)
    ]
    return slide


def _spans_de_texto(page: pymupdf.Page) -> list[SpanPymupdf]:
    # type 0 = texto, 1 = imagem (imagens ficam para a T15)
    blocos_brutos = page.get_text("dict")["blocks"]
    blocos_de_texto = [bruto for bruto in blocos_brutos if bruto["type"] == 0]
    return [
        span
        for bloco in blocos_de_texto
        for linha in bloco["lines"]
        for span in linha["spans"]
        if span["text"].strip()
    ]


def span_para_bloco(
    span: SpanPymupdf, matriz: pymupdf.Matrix, largura: float, altura: float
) -> Bloco:
    """Converte um span do PyMuPDF em ``Bloco`` com bbox normalizado (0–1) e já rotacionado

    Exemplo: ``span_para_bloco(span, page.rotation_matrix, page.rect.width, page.rect.height)``

    :param span: span vindo de ``page.get_text("dict")``
    :param matriz: ``page.rotation_matrix``, que corrige páginas giradas
    :param largura: largura visual da página, em pontos
    :param altura: altura visual da página, em pontos
    :return: ``Bloco`` com texto, posição relativa e sinais de estilo
    """
    caixa = pymupdf.Rect(span["bbox"]) * matriz
    return Bloco(
        texto=span["text"],
        bbox=(
            caixa.x0 / largura,
            caixa.y0 / altura,
            caixa.x1 / largura,
            caixa.y1 / altura,
        ),
        tamanho=span["size"],
        fonte=span["font"],
        negrito=bool(span["flags"] & pymupdf.TEXT_FONT_BOLD),
        cor=span["color"],
    )
