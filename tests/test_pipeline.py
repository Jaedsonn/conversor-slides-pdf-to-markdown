from pathlib import Path

import pytest

from conversor.estrategias import ESTRATEGIAS
from conversor.main import converter_lote, criar_parser, main
from conversor.pipeline import ContextoConversao, converter_pdf, listar_pdfs
from tests.fakes import ExtratorFalso

ARQUIVO = "teoria/04 - Conectividade.pdf"


def _contexto(tmp_path: Path, extrator: ExtratorFalso) -> ContextoConversao:
    return ContextoConversao(
        pasta_pdf=Path("pdf"),
        pasta_md=tmp_path,
        mapa_arquivos={ARQUIVO: "bruno_gslides"},
        extrator=extrator,
        estrategias=ESTRATEGIAS,
    )


def test_main_converte_um_arquivo_real(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Integração: lê o PDF real 04 e o grupos.json do repositório
    main(["--arquivo", ARQUIVO, "--md", str(tmp_path)])
    assert (tmp_path / "04-conectividade.md").exists()
    assert "Pronto: 1 arquivo(s)" in capsys.readouterr().out


def test_converter_pdf_classifica_extrai_e_grava(tmp_path: Path) -> None:
    extrator = ExtratorFalso()
    destino = converter_pdf(ARQUIVO, _contexto(tmp_path, extrator))
    assert extrator.chamadas == [(f"pdf/{ARQUIVO}", "bruno_gslides")]
    assert destino == tmp_path / "04-conectividade.md"
    assert "Olá" in destino.read_text(encoding="utf-8")


def test_converter_pdf_nao_mapeado_falha_antes_de_extrair(tmp_path: Path) -> None:
    extrator = ExtratorFalso()
    with pytest.raises(ValueError, match="99 - Falso"):
        converter_pdf("teoria/99 - Falso.pdf", _contexto(tmp_path, extrator))
    assert extrator.chamadas == []


def test_converter_lote_informa_progresso(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    gerados = converter_lote([ARQUIVO], _contexto(tmp_path, ExtratorFalso()))
    assert gerados == [tmp_path / "04-conectividade.md"]
    assert f"[1/1] {ARQUIVO}" in capsys.readouterr().out


def test_listar_pdfs_relativos_e_ordenados(tmp_path: Path) -> None:
    (tmp_path / "teoria").mkdir()
    (tmp_path / "teoria" / "b.pdf").touch()
    (tmp_path / "a.pdf").touch()
    (tmp_path / "notas.txt").touch()
    assert listar_pdfs(tmp_path) == ["a.pdf", "teoria/b.pdf"]


def test_parser_exige_arquivo_ou_todos() -> None:
    parser = criar_parser()
    assert parser.parse_args(["--todos"]).todos is True
    assert parser.parse_args(["--arquivo", ARQUIVO]).arquivo == ARQUIVO
    with pytest.raises(SystemExit):
        parser.parse_args([])
