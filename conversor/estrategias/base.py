from abc import ABC, abstractmethod

from conversor.modelo import Aula, Slide


class Estrategia(ABC):
    """Tratamento específico de um grupo de estilo (Template Method)"""

    def processar(self, aula: Aula) -> Aula:
        """Ordem FIXA para todos os grupos. As subclasses só preenchem os passos

        Exemplo: ``Bruno().processar(extrair(pdf, "bruno_gslides"))``

        :param aula: aula recém-extraída, com slides sem título
        :return: a mesma aula com títulos preenchidos e já limpa
        """

        for slide in aula.slides:
            slide.titulo = self.achar_titulo(slide)
        return self.limpar(aula)

    @abstractmethod
    def achar_titulo(self, slide: Slide) -> str:
        """Lê o título de um slide com os blocos ainda crus (antes de ``limpar``)

        Exemplo: ``Cid().achar_titulo(slide)`` → ``"Provas de NP -completude: CV (cont.)"``

        :param slide: slide recém-extraído
        :return: título do slide, ou ``""`` se não houver
        """

    def limpar(self, aula: Aula) -> Aula:
        """Remove o ruído do grupo; o padrão não altera nada até as tasks da Fase 2

        Exemplo: ``Hamilton().limpar(aula)``

        :param aula: aula com títulos já preenchidos
        :return: a aula limpa
        """
        return aula
