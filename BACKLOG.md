# Backlog — Conversor de slides MATA53 → Markdown

Objetivo: transformar os 26 PDFs (4 grupos de estilo, ver `ANALISE-ESTILOS.md`) em Markdown limpo + figuras + `CLAUDE.md` de índice, para uso eficiente no Claude Code.

**Como usar:** execute uma task por vez, na ordem. Cada task tem **critério de pronto** — só marque `[x]` quando todos forem verdadeiros. Faça um commit por task (`T03: extrair texto com posição`).

Legenda: 🎓 = conceito que você vai praticar · ⛓️ = depende de

---

## Fase 0 — Fundação

### [ ] T00 — Organizar o projeto e versionar
- Mover `teoria/` e `algoritmos/` para `pdf/teoria/` e `pdf/algoritmos/`; atualizar caminhos no `grupos.json`.
- Criar `conversor/`, `md/`, `figuras/`, `.cache/`.
- `git init` + `.gitignore` (ignorar `.cache/`, `.venv/`, `__pycache__/`; **versionar** `md/` e `figuras/` para ver diffs da saída).
- **Pronto quando:** `git status` limpo após o primeiro commit; `grupos.json` aponta para `pdf/...` e todos os 26 existem.
- 🎓 estrutura de projeto, por que versionar a saída gerada.

### [ ] T01 — Ambiente Python com uv
- `uv init` dentro de `conversor/`; dependências: `pymupdf`, `pillow`; dev: `pytest`.
- **Pronto quando:** `uv run python -c "import fitz; print(fitz.__version__)"` funciona.
- 🎓 ambientes isolados, lockfile (`uv.lock`) e reprodutibilidade.
- ⛓️ T00

### [ ] T02 — Modelo de dados (representação intermediária)
- `modelo.py` com dataclasses: `Bloco(texto, bbox, tamanho, fonte)`, `Figura(caminho, pagina, bbox)`, `Slide(pdf, pagina, titulo, blocos, figuras, precisa_render)`, `Aula(id, titulo, autor, grupo, slides)`.
- **Pronto quando:** teste cria um `Slide` manualmente e verifica campos e valores padrão.
- 🎓 dataclasses, representação intermediária, tipagem.
- ⛓️ T01

---

## Fase 1 — Pipeline genérico

### [ ] T03 — Extrator genérico (PyMuPDF)
- `extrair.py`: `extrair(pdf) -> list[Slide]` usando `page.get_text("dict")`; preencher `blocos` com bbox/fonte/tamanho; título = maior fonte no topo.
- Normalizar bbox para **proporção da página** (0–1), pois os grupos têm tamanhos diferentes.
- **Pronto quando:** rodando em 1 PDF de cada grupo (`04`, `16A`, `17b`, `16-notes`) imprime nº de slides correto e títulos plausíveis; notas retornam slides sem blocos.
- 🎓 bounding boxes, coordenadas normalizadas.
- ⛓️ T02

### [ ] T04 — Classificador de grupo
- `classificar(pdf) -> str`: primeiro pelo `grupos.json`; senão pela `assinatura` (tamanho da página, Producer/Creator); senão **erro explícito**.
- **Pronto quando:** teste parametrizado cobre os 26 arquivos + um PDF falso que deve levantar exceção.
- 🎓 fail loudly, testes parametrizados (`pytest.mark.parametrize`).
- ⛓️ T03

### [ ] T05 — Interface de estratégia + estratégia nula
- `estrategias/base.py`: classe abstrata `Estrategia.limpar(slides) -> list[Slide]`; `EstrategiaNula` que devolve sem alterar.
- Registro `{"bruno_gslides": ..., "hamilton_beamer": ..., ...}` usando a nula por enquanto.
- **Pronto quando:** pipeline roda de ponta a ponta com a nula sem erro.
- 🎓 Strategy Pattern, ABC, Open/Closed.
- ⛓️ T04

### [ ] T06 — Escritor de Markdown (versão mínima)
- `escrever.py`: `Aula -> .md` com cabeçalho (fonte, autor), `## título (slide N)` por slide e referência às figuras.
- Nome do arquivo: `NN-slug.md` (ex.: `04-conectividade.md`).
- **Pronto quando:** gera `md/04-conectividade.md` legível (ainda com lixo — normal).
- 🎓 slugify, separação extração × apresentação.
- ⛓️ T05

### [ ] T07 — CLI e Makefile
- `main.py` com `argparse`: `converter [--arquivo X] [--grupo G] [--todos]`.
- `Makefile`: `converter`, `testar`, `limpar`.
- **Pronto quando:** `make converter` gera os 26 `.md` (sujos) e `make testar` passa.
- 🎓 CLI, automação de tarefas.
- ⛓️ T06

### [ ] T08 — Utilitários de texto compartilhados
- `texto.py`: `normalizar_acentos` (NFC + `ı́`→`í` etc.), `remover_por_faixa(blocos, y_min, y_max)`, `colapsar_espacos`.
- **Pronto quando:** testes: `"saı́da"` → `"saída"`; bloco com y=0.95 é removido pela faixa de rodapé.
- 🎓 Unicode (NFC vs NFD, caracteres combinantes), DRY.
- ⛓️ T07

---

## Fase 2 — Estratégias por grupo

### [ ] T09 — Hamilton: acentos, rodapé, barra de navegação
- Normalizar acentos; remover rodapé `Hamilton José Brumatto PAA` e a barra de seções no topo (faixa superior + fonte pequena).
- **Pronto quando:** em `md/16a-*.md` não aparece `PAA`, nem `ı́`, nem a lista de seções repetida; `grep -c "saída"` > 0.
- 🎓 limpeza espacial vs. por regex.
- ⛓️ T08

### [ ] T10 — Hamilton: overlays
- Colapsar sequências em que o texto do slide n é prefixo do n+1 (manter o último).
- Decidir o caso "texto igual, desenho muda" (desafio da conversa anterior) — documentar a decisão no código.
- **Pronto quando:** `16B` cai de 25 para ~13 slides; teste com 3 slides sintéticos cobre o colapso.
- 🎓 deduplicação, heurísticas com limiares nomeados.
- ⛓️ T09

### [ ] T11 — Hamilton: detectar grafos desenhados
- Heurística: muitos spans curtos (≤2 chars) espalhados → `precisa_render=True` e descartar esse texto picado.
- **Pronto quando:** página 10 do `11a` (BFS) é marcada; páginas só de texto do `16A` não são.
- 🎓 heurística, falso positivo × falso negativo.
- ⛓️ T10

### [ ] T12 — Renderizador de páginas
- `render.py`: páginas com `precisa_render` → `figuras/<aula>-p<N>.png` (dpi configurável), com Pillow para otimizar tamanho.
- **Pronto quando:** PNGs gerados para as páginas marcadas e referenciados no `.md`.
- 🎓 rasterização, DPI, trade-off qualidade × tamanho.
- ⛓️ T11

### [ ] T13 — Cid: cabeçalho, rodapé, glifos
- Reaproveitar `normalizar_acentos`; remover `NP-completude N` e `Cid C. de Souza`; tabela de substituições (`B ` → `▷ `, `N P` → `NP`, …); páginas com pouco texto → `precisa_render`.
- **Pronto quando:** `md/17b-*.md` sem `Cid C. de Souza`, sem `N P-`, com `▷`.
- 🎓 tabela de substituições, reaproveitamento entre estratégias.
- ⛓️ T12

### [ ] T14 — Bruno: rodapé e numeração
- Remover rodapé pela faixa inferior; usar sempre o número da **página do PDF** (ignorar o 378 do iLovePDF).
- **Pronto quando:** nenhum `.md` do grupo contém `UFBA/IC/DCC` ou `Bruno Santos`.
- ⛓️ T08

### [ ] T15 — Bruno: imagens do template × figuras de conteúdo
- Contar em quantas páginas cada `xref` aparece; >80% → template (descartar); demais → extrair para `figuras/`.
- **Pronto quando:** `04` não gera 53 logos; gera só figuras de conteúdo; teste da função de contagem.
- 🎓 frequência como sinal, hashing/identidade de objetos.
- ⛓️ T14, T12

### [ ] T16 — Bruno: caracteres perdidos `(` e `–`
- Comparar saída do PyMuPDF com o `pdftotext`; se ainda faltar, heurística de reparo (`X DFS)` → `X (DFS)`) e OCR **só da faixa do título** como plano B (Tesseract).
- **Pronto quando:** contagem de `(` e `)` balanceada (±2) em todos os 13 arquivos do grupo.
- 🎓 diagnóstico de ToUnicode/fontes, medir antes de corrigir.
- ⛓️ T15

### [ ] T17 — Bruno: juntar slides continuados `(k)`
- Slides seguidos com mesmo título sem o sufixo `(k)` → uma seção `## Título (slides 12–14)`.
- **Pronto quando:** em `08` as seções `Depth-First Search (DFS)` aparecem uma vez só.
- ⛓️ T16

### [ ] T18 — Notas manuscritas: render + transcrição com visão
- Renderizar páginas (~150 dpi, reduzidas com Pillow); transcrever com Claude (visão) pedindo Markdown + LaTeX para fórmulas.
- **Cache** em `.cache/<sha256-da-imagem>.md` — não retranscrever o que já existe.
- Decidir: Claude API (`ANTHROPIC_API_KEY`, custo por página) **ou** transcrição feita no próprio Claude Code lendo os PNGs.
- **Pronto quando:** `md/16-notes.md` legível; rodar 2× não faz novas chamadas.
- 🎓 idempotência, cache por hash de conteúdo, custo de API.
- ⛓️ T12

---

## Fase 3 — Qualidade

### [ ] T19 — Relatório de qualidade
- `make relatorio`: por aula → nº de slides antes/depois, chars, figuras, páginas renderizadas, avisos (parênteses desbalanceados, `ı́` restante, rodapé restante).
- **Pronto quando:** relatório sem avisos ou com avisos justificados.
- 🎓 métricas como contrato, observabilidade.
- ⛓️ T13, T17, T18

### [ ] T20 — Testes de regressão (snapshot)
- Para 1 aula de cada grupo, salvar o `.md` esperado em `tests/snapshots/` e comparar na suite.
- **Pronto quando:** `make testar` falha se qualquer mudança alterar a saída sem atualizar o snapshot.
- 🎓 golden files, regressão.
- ⛓️ T19

### [ ] T21 — Revisão manual por amostragem
- Abrir 3 páginas aleatórias de cada grupo: PDF lado a lado com o `.md`; anotar problemas → viram tasks novas ou ajustes de limiar.
- **Pronto quando:** checklist de 12 páginas revisadas registrada no fim deste arquivo.
- 🎓 validação humana — métricas não pegam tudo.
- ⛓️ T20

---

## Fase 4 — Entrega

### [ ] T22 — Índice `CLAUDE.md` gerado
- Gerar a partir das aulas: por aula → título, autor, 3–6 tópicos (títulos das seções), caminho do `.md`, caminho do PDF.
- Incluir instruções de uso: "leia o `.md`; abra o PDF/figura só se precisar do desenho".
- **Pronto quando:** `CLAUDE.md` < 300 linhas e cobre as 26 aulas.
- 🎓 context engineering — índice barato, conteúdo sob demanda.
- ⛓️ T21

### [ ] T23 — Medir o ganho de contexto
- Comparar tokens estimados (chars/4): PDFs brutos × `md/` final; registrar no `README`.
- **Pronto quando:** números registrados (meta: < 180 mil tokens no total).
- ⛓️ T22

### [ ] T24 — README do projeto
- Como instalar, rodar, adicionar um PDF novo (e um grupo novo), decisões de design e limitações conhecidas.
- **Pronto quando:** alguém (ou você daqui a 2 meses) consegue rodar só lendo o README.
- ⛓️ T23

### [ ] T25 — ✅ Task final: teste de aceitação com o Claude Code
- Abrir uma sessão nova do Claude Code em `~/claude/ufba/grafos` e fazer 3 perguntas reais de estudo, ex.:
  1. "Explique a diferença entre Kosaraju e Tarjan usando os slides da disciplina."
  2. "Qual a relação entre Spanning Tree e o algoritmo de Prim nas aulas?"
  3. "Resuma as anotações manuscritas sobre análise de algoritmos."
- **Pronto quando:** o Claude encontra as aulas certas pelo índice, cita arquivo/slide, responde corretamente **sem abrir os PDFs** (exceto para figuras), e o projeto está commitado com tag `v1.0`.
- ⛓️ T24

---

## Futuro (fora do escopo v1)
- Detectar automaticamente slides novos publicados no AVA e reconverter só o que mudou.
- Grafo de conhecimento com `/graphify` usando `md/` como entrada.
- Gerar flashcards/listas de exercícios a partir das aulas.

## Registro da revisão manual (T21)
| Grupo | Aula | Página | Problema | Ação |
|---|---|---|---|---|
