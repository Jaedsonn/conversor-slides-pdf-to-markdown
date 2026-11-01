import pymupdf
import pytest

from conversor.extrair import SpanPymupdf, extrair, ler_identificacao, span_para_bloco


def test_ler_identificacao_separa_id_e_titulo() -> None:
    assert ler_identificacao("pdf/algoritmos/16A - Algoritmos.pdf") == (
        "16A",
        "Algoritmos",
    )


def test_ler_identificacao_fora_do_padrao_falha_com_nome() -> None:
    with pytest.raises(ValueError, match=r"'slides'.*<id> - <titulo>\.pdf"):
        ler_identificacao("pdf/slides.pdf")


def test_span_para_bloco_normaliza_bbox_e_le_negrito() -> None:
    span = SpanPymupdf(
        text="Grafo",
        bbox=(10.0, 20.0, 30.0, 40.0),
        size=12.0,
        font="Inter-Bold",
        flags=pymupdf.TEXT_FONT_BOLD,
        color=0xEC1015,
    )
    bloco = span_para_bloco(span, pymupdf.Identity, largura=100.0, altura=200.0)
    assert bloco.bbox == (0.1, 0.1, 0.3, 0.2)
    assert bloco.negrito is True
    assert (bloco.texto, bloco.tamanho, bloco.cor) == ("Grafo", 12.0, 0xEC1015)


def test_extrair_corrige_rotacao_do_cid() -> None:
    # Integração (lê PDF real): 17b tem rotation=270; rodapé deve ficar embaixo
    # Página 5 e não 1: a capa traz o nome do autor no meio da página
    aula = extrair("pdf/algoritmos/17b - NP-Completude.pdf", "cid_latex")
    rodape = [bloco for bloco in aula.slides[4].blocos if "Souza" in bloco.texto]
    assert rodape and all(bloco.bbox[1] > 0.9 for bloco in rodape)
