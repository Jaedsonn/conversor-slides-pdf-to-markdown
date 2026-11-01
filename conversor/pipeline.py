"""Orquestra um PDF de ponta a ponta: classificar → extrair → estratégia → escrever"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from conversor.classificar import classificar
from conversor.escrever import salvar_markdown
from conversor.estrategias import estrategia_para
from conversor.estrategias.base import Estrategia
from conversor.modelo import Aula

# Assinatura de ``conversor.extrair.extrair``; injetada para os testes não lerem PDF
Extrator = Callable[[str, str], Aula]


@dataclass
class ContextoConversao:
    """Dependências de uma conversão, montadas uma vez pela CLI"""

    pasta_pdf: Path
    pasta_md: Path
    mapa_arquivos: dict[str, str]
    extrator: Extrator
    estrategias: dict[str, Estrategia]


def listar_pdfs(pasta_pdf: Path) -> list[str]:
    """Lista os PDFs sob ``pasta_pdf``, como caminhos relativos a ela, em ordem

    Exemplo: ``listar_pdfs(Path("pdf"))[0]`` → ``"algoritmos/11a - BFS-DFS-Kosaraju-Tarjan.pdf"``

    :param pasta_pdf: raiz dos PDFs (ex.: ``pdf/``)
    :return: caminhos relativos com ``/``
    """
    pdfs = pasta_pdf.rglob("*.pdf")
    return sorted(pdf.relative_to(pasta_pdf).as_posix() for pdf in pdfs)


def converter_pdf(caminho_relativo: str, contexto: ContextoConversao) -> Path:
    """Converte um PDF em Markdown e devolve o arquivo gerado

    Exemplo: ``converter_pdf("teoria/04 - Conectividade.pdf", contexto)`` → ``Path("md/04-conectividade.md")``

    :param caminho_relativo: caminho do PDF relativo a ``contexto.pasta_pdf``
    :param contexto: pastas, mapa de grupos, extrator e estratégias a usar
    :return: caminho do .md gravado
    """
    grupo = classificar(caminho_relativo, contexto.mapa_arquivos)
    estrategia = estrategia_para(grupo, contexto.estrategias)
    pdf = (contexto.pasta_pdf / caminho_relativo).as_posix()
    aula = estrategia.processar(contexto.extrator(pdf, grupo))
    return salvar_markdown(aula, contexto.pasta_md)
