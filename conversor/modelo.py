from dataclasses import dataclass, field


@dataclass
class Bloco:
    """Um trecho de texto e onde ele está na página"""

    texto: str
    tamanho: float
    bbox: tuple[float, float, float, float]
    cor: int
    negrito: bool
    fonte: str


@dataclass
class Figura:
    """Uma imagem ou figura do slide"""

    caminho: str
    origem: str


@dataclass
class Slide:
    """Uma página do slide"""

    pdf: str
    pagina: int
    titulo: str = ""
    blocos: list[Bloco] = field(default_factory=list)
    figuras: list[Figura] = field(default_factory=list)
    precisa_render: bool = False


@dataclass
class Aula:
    """Um conjunto de slides de uma aula"""

    id: str
    titulo: str
    grupo: str
    # Caminho do PDF de origem: o escritor cita a fonte no cabeçalho do .md
    pdf: str = ""
    slides: list[Slide] = field(default_factory=list)
