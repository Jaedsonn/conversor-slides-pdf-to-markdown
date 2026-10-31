from dataclasses import dataclass, field
from typing import List

@dataclass
class Bloco:
    """Um trecho de texto e onde ele está na página"""
    
    texto: str
    tamanho: float
    bbox: tuple[float, float, float, float]
    
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
    blocos: List[Bloco] = field(default_factory=list)
    figuras: List[Figura] = field(default_factory=list)
    precise_render: bool = False

class Aula:
    """Um conjunto de slides de uma aula"""
    id: str
    titulo: str
    grupo: str
    slides: List[Slide] = field(default_factory=list)