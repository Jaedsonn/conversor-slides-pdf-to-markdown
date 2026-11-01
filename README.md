# Conversor de Slides

Transforma os slides em PDF da disciplina **MATA53 – Teoria dos Grafos (UFBA)** em arquivos de texto (Markdown), para estudar com a ajuda do Claude Code.

## De onde veio

1. Entramos no **AVA da UFBA** (ava.ufba.br) e baixamos os slides das abas **Teoria** e **Algoritmos** da turma de Grafos: 26 PDFs, 1.256 páginas.
2. Surgiu a dúvida: dá para o Claude estudar direto pelos PDFs?
3. Dá, mas sai caro. Para o Claude, cada página de PDF vale quase como uma imagem. Lidas assim, as 1.256 páginas custariam cerca de **1,5 a 2 milhões de tokens**. Em texto puro, o mesmo conteúdo fica em torno de **200 mil**.
4. Daí veio a ideia de **converter tudo para texto** e criar um índice. Assim o Claude abre só a aula de que precisa.

## O problema: os PDFs não são iguais

Os slides foram feitos por professores diferentes, com ferramentas diferentes. Quando analisamos os 26 arquivos, eles caíram em **4 grupos**:

| Grupo | Quem fez | Como | O que atrapalha |
|---|---|---|---|
| `bruno_gslides` | Prof. Bruno Santos | Google Slides | rodapé em toda página; figuras são imagens; `(` vira um caractere estranho |
| `hamilton_beamer` | Prof. Hamilton Brumatto | LaTeX (Beamer) | acentos quebrados (`M´etodos`); menu no topo; o mesmo slide repetido várias vezes |
| `cid_latex` | Prof. Cid de Souza | LaTeX | página girada; símbolos trocados |
| `notas_manuscritas` | anotações à mão (iPad) | imagem | não tem texto nenhum |

Por isso cada grupo recebe um **tratamento próprio**. O arquivo `grupos.json` diz a qual grupo cada PDF pertence.

## Como funciona

Cada PDF passa por 4 etapas:

```
PDF ─► 1. Classificar ─► 2. Extrair ─► 3. Tratar ─► 4. Escrever ─► .md
       (qual grupo?)     (copia o      (regras do    (gera o
                          texto e a     grupo: acha   Markdown)
                          posição)      o título...)
```

1. **Classificar:** consulta o `grupos.json` para saber de qual grupo é o PDF.
2. **Extrair:** lê cada página e guarda cada pedaço de texto com a **posição**, o **tamanho**, a **fonte** e a **cor**. Aqui nada é limpo, só copiado.
3. **Tratar:** aplica as regras do grupo. Por enquanto, só acha o título de cada slide, e cada professor marca o título de um jeito:
   - **Bruno:** é o texto com a **maior letra** no topo.
   - **Hamilton:** é o item **destacado em branco** no menu do topo.
   - **Cid:** é a primeira linha em **negrito**.
4. **Escrever:** gera um `.md` por aula na pasta `md/`.

## Como usar

Converter todos os PDFs:

```bash
make converter
```

Converter um PDF só:

```bash
uv run python -m conversor --arquivo "teoria/04 - Conectividade.pdf"
```

Rodar os testes:

```bash
make testar
```

## Pastas

```
pdf/            os 26 PDFs originais (teoria/ e algoritmos/)
md/             o resultado: um .md por aula
conversor/      o código
  estrategias/  as regras de cada grupo
tests/          os testes
grupos.json     qual PDF pertence a qual grupo
BACKLOG.md      a lista de tarefas, da primeira até a última
CODE_STYLE.md   as regras de escrita do código
```

## Onde estamos

- ✅ O caminho completo funciona: os 26 PDFs viram 26 arquivos `.md`.
- ✅ O título de cada slide é encontrado nos 4 grupos.
- ⏳ O texto ainda sai "sujo": rodapés, acentos quebrados e slides repetidos continuam lá. A limpeza de cada grupo são as próximas tarefas do `BACKLOG.md`.
- 🎯 **Objetivo final:** abrir o Claude Code nesta pasta, perguntar algo como *"qual a diferença entre Kosaraju e Tarjan?"* e ele responder usando as aulas, sem precisar abrir os PDFs.
