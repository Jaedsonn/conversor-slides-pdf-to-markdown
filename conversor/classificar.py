"""Decide o grupo de estilo de cada PDF a partir do ``grupos.json``"""

import json
import unicodedata
from pathlib import Path


def _chave_de_arquivo(caminho_relativo: str) -> str:
    # NFC: nomes com acento ("Árvores") podem vir decompostos (NFD) do sistema
    # de arquivos e não casariam com as chaves do JSON
    return unicodedata.normalize("NFC", Path(caminho_relativo).as_posix())


def carregar_mapa_arquivos(caminho_json: Path) -> dict[str, str]:
    """Lê o mapa ``arquivo -> grupo`` da seção ``"arquivos"`` do ``grupos.json``

    Exemplo: ``carregar_mapa_arquivos(Path("grupos.json"))["teoria/04 - Conectividade.pdf"]``

    :param caminho_json: caminho do ``grupos.json``
    :return: dicionário com caminhos relativos a ``pdf/`` como chave e grupo como valor
    :raises ValueError: se o JSON não tiver a seção ``"arquivos"``
    """
    config = json.loads(caminho_json.read_text(encoding="utf-8"))
    arquivos = config.get("arquivos")
    if not isinstance(arquivos, dict):
        raise ValueError(
            f"{caminho_json} sem seção 'arquivos' válida (veio {type(arquivos).__name__}). "
            'Esperado: {"arquivos": {"teoria/04 - Conectividade.pdf": "bruno_gslides"}}.'
        )
    return {_chave_de_arquivo(caminho): grupo for caminho, grupo in arquivos.items()}


def classificar(caminho_relativo: str, mapa_arquivos: dict[str, str]) -> str:
    """Devolve o grupo de estilo de um PDF; falha alto se ele não estiver mapeado

    Exemplo: ``classificar("teoria/04 - Conectividade.pdf", mapa)`` → ``"bruno_gslides"``

    :param caminho_relativo: caminho do PDF relativo a ``pdf/``
    :param mapa_arquivos: saída de ``carregar_mapa_arquivos``
    :return: nome do grupo (ex.: ``"hamilton_beamer"``)
    :raises ValueError: se o arquivo não estiver no mapa
    """
    chave = _chave_de_arquivo(caminho_relativo)
    if chave not in mapa_arquivos:
        raise ValueError(
            f"PDF sem grupo: {chave!r}. Esperado um caminho relativo a pdf/ listado "
            "em grupos.json -> 'arquivos', ex.: 'teoria/04 - Conectividade.pdf'."
        )
    return mapa_arquivos[chave]
