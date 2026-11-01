"""Apresentação: transforma uma ``Aula`` em Markdown (puro) e grava o arquivo (I/O)"""

import re
import unicodedata
from pathlib import Path

from conversor.linhas import juntar_linhas
from conversor.modelo import Aula, Slide


def slugificar(texto: str) -> str:
    """Gera um trecho de nome de arquivo: minúsculo, sem acento, só ``a-z0-9`` e ``-``

    Exemplo: ``slugificar("06 Árvores")`` → ``"06-arvores"``

    :param texto: texto livre
    :return: slug sem hífens nas pontas
    """
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(
        caractere for caractere in decomposto if not unicodedata.combining(caractere)
    )
    return re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-")


def nome_do_markdown(aula: Aula) -> str:
    """Nome do .md no formato ``NN-slug.md``

    Exemplo: ``nome_do_markdown(Aula("04", "Conectividade", "bruno_gslides"))`` → ``"04-conectividade.md"``

    :param aula: aula com ``id`` e ``titulo``
    :return: nome do arquivo, sem diretório
    """
    return f"{slugificar(f'{aula.id} {aula.titulo}')}.md"


def _renderizar_slide(slide: Slide) -> str:
    titulo = slide.titulo or f"Slide {slide.pagina}"
    corpo = juntar_linhas(slide.blocos, separador="\n")
    cabecalho = f"## {titulo} (slide {slide.pagina})"
    return f"{cabecalho}\n\n{corpo}" if corpo else cabecalho


def renderizar_markdown(aula: Aula) -> str:
    """Converte a aula em texto Markdown, sem tocar no disco

    Exemplo: ``renderizar_markdown(aula).startswith("# 04 — Conectividade")``

    :param aula: aula já processada pela estratégia do grupo
    :return: Markdown completo, terminado em quebra de linha
    """
    cabecalho = (
        f"# {aula.id} — {aula.titulo}\n\n> Fonte: `{aula.pdf}` · grupo: `{aula.grupo}`"
    )
    secoes = [cabecalho] + [_renderizar_slide(slide) for slide in aula.slides]
    return "\n\n".join(secoes) + "\n"


def salvar_markdown(aula: Aula, pasta_md: Path) -> Path:
    """Grava o Markdown da aula em ``pasta_md/NN-slug.md`` (sobrescreve)

    Exemplo: ``salvar_markdown(aula, Path("md"))`` → ``Path("md/04-conectividade.md")``

    :param aula: aula já processada
    :param pasta_md: diretório de saída; é criado se não existir
    :return: caminho do arquivo gravado
    """
    pasta_md.mkdir(parents=True, exist_ok=True)
    destino = pasta_md / nome_do_markdown(aula)
    destino.write_text(renderizar_markdown(aula), encoding="utf-8")
    return destino
