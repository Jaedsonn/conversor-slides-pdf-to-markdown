"""CLI: ``uv run python -m conversor --todos`` ou ``--arquivo "teoria/04 - Conectividade.pdf"``"""

import argparse
from pathlib import Path

from conversor.classificar import carregar_mapa_arquivos
from conversor.estrategias import ESTRATEGIAS
from conversor.extrair import extrair
from conversor.pipeline import ContextoConversao, converter_pdf, listar_pdfs


def criar_parser() -> argparse.ArgumentParser:
    """Monta o parser da CLI; ``--arquivo`` e ``--todos`` são mutuamente exclusivos

    Exemplo: ``criar_parser().parse_args(["--todos"]).todos`` → ``True``

    :return: parser configurado
    """
    parser = argparse.ArgumentParser(
        prog="conversor", description="PDF de slides → Markdown"
    )
    alvo = parser.add_mutually_exclusive_group(required=True)
    alvo.add_argument(
        "--arquivo", help="PDF relativo a pdf/, ex.: 'teoria/04 - Conectividade.pdf'"
    )
    alvo.add_argument(
        "--todos", action="store_true", help="converte todos os PDFs de pdf/"
    )
    parser.add_argument("--pdf", type=Path, default=Path("pdf"), help="pasta dos PDFs")
    parser.add_argument("--md", type=Path, default=Path("md"), help="pasta de saída")
    parser.add_argument(
        "--grupos", type=Path, default=Path("grupos.json"), help="mapa de grupos"
    )
    return parser


def converter_lote(arquivos: list[str], contexto: ContextoConversao) -> list[Path]:
    """Converte vários PDFs mostrando o progresso em texto simples

    Exemplo: ``converter_lote(["teoria/04 - Conectividade.pdf"], contexto)``

    :param arquivos: caminhos relativos a ``contexto.pasta_pdf``
    :param contexto: dependências da conversão
    :return: arquivos .md gerados, na mesma ordem
    """
    gerados: list[Path] = []
    for posicao, arquivo in enumerate(arquivos, start=1):
        destino = converter_pdf(arquivo, contexto)
        print(f"[{posicao}/{len(arquivos)}] {arquivo} -> {destino}")
        gerados.append(destino)
    return gerados


def main(argv: list[str] | None = None) -> None:
    """Ponto de entrada da CLI

    Exemplo: ``main(["--arquivo", "teoria/04 - Conectividade.pdf"])``

    :param argv: argumentos (``None`` usa ``sys.argv``)
    """
    args = criar_parser().parse_args(argv)
    contexto = ContextoConversao(
        pasta_pdf=args.pdf,
        pasta_md=args.md,
        mapa_arquivos=carregar_mapa_arquivos(args.grupos),
        extrator=extrair,
        estrategias=ESTRATEGIAS,
    )
    arquivos = listar_pdfs(args.pdf) if args.todos else [args.arquivo]
    gerados = converter_lote(arquivos, contexto)
    print(f"Pronto: {len(gerados)} arquivo(s) em {args.md}/")
