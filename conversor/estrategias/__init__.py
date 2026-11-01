from conversor.estrategias.achar_titulo import Bruno, Cid, Hamilton, Notas
from conversor.estrategias.base import Estrategia

# Registro padrão, montado pela CLI e injetado no pipeline (ContextoConversao)
ESTRATEGIAS: dict[str, Estrategia] = {
    "bruno_gslides": Bruno(),
    "hamilton_beamer": Hamilton(),
    "cid_latex": Cid(),
    "notas_manuscritas": Notas(),
}


def estrategia_para(grupo: str, estrategias: dict[str, Estrategia]) -> Estrategia:
    """Devolve a estratégia registrada para um grupo de estilo

    Exemplo: ``estrategia_para("cid_latex", ESTRATEGIAS).processar(aula)``

    :param grupo: chave do grupo, como em ``grupos.json``
    :param estrategias: registro ``grupo -> Estrategia`` (normalmente ``ESTRATEGIAS``)
    :return: instância de ``Estrategia`` do grupo
    :raises ValueError: se o grupo não estiver no registro
    """
    if grupo not in estrategias:
        raise ValueError(
            f"Grupo desconhecido: {grupo!r}. Esperado um de {sorted(estrategias)}. "
            "Adicione em ESTRATEGIAS."
        )
    return estrategias[grupo]
