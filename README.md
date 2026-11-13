# Elo — cuidado compartilhado

O Elo é um protótipo local para ajudar famílias a organizar o cuidado de idosos e pessoas dependentes. A proposta é transformar uma responsabilidade que costuma ficar concentrada em uma pessoa em uma rede mais equilibrada, acolhedora e organizada.

## Executar

Requisitos: Python 3.10 ou superior. A aplicação usa somente a biblioteca padrão do Python, sem instalação de pacotes.

```powershell
python app.py
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000) no navegador. Encerre o servidor com `Ctrl+C`.

## Funcionalidades demonstradas

- Visão geral com tarefas, agenda e participação da família.
- Distribuição de tarefas considerando duração, carga já assumida e disponibilidade semanal de cada familiar.
- Questionário visual de bem-estar e painel de impacto para acompanhar a colaboração.
- Busca de serviços de apoio por necessidade, usando uma rede modelada como grafo.
- Registro de tarefas concluídas, inclusão de novas tarefas e compromissos.
- Protótipos visuais de lembretes e integração com WhatsApp. Os serviços externos ainda não estão conectados.

## Onde estão as partes do trabalho

- **Algoritmos em Python:** `app.py`. A função `distribuir_com_memoizacao` implementa memoização e `distribuir_com_tabulacao` implementa tabulação.
- **Grafo e busca de apoio:** também em `app.py`, nas estruturas `GRAFO_APOIO` e `SERVICOS_APOIO` e na função `buscar_caminhos_de_apoio`.
- **Interface:** `web/index.html` estrutura as telas, `web/styles.css` define o visual e `web/app.js` cuida das interações.
- **Esta documentação:** explica a proposta e as técnicas aplicadas.

O navegador se comunica com o servidor Python por três rotas locais: `/api/overview` carrega os dados, `/api/allocate` calcula a divisão das tarefas e `/api/support` busca serviços na rede de apoio. Os nomes dos campos JSON, como `members` e `tasks`, são mantidos em inglês para corresponder ao formato que a interface envia e recebe. Os métodos `do_GET` e `do_POST` também ficam com esses nomes porque fazem parte da interface padrão da biblioteca HTTP do Python.

## Programação dinâmica e grafos

O distribuidor minimiza a maior proporção de tempo comprometido entre os familiares e usa a soma dos quadrados dessas proporções para desempatar planos. Antes de calcular, valida se as tarefas cabem na disponibilidade de cada pessoa.

- **Memoização:** `distribuir_com_memoizacao` resolve recursivamente os estados `(familiar, tarefas restantes)` e armazena resultados com `functools.lru_cache`.
- **Tabulação:** `distribuir_com_tabulacao` constrói iterativamente os melhores estados para cada subconjunto de tarefas já atribuído.
- **Grafos:** `buscar_caminhos_de_apoio` percorre a rede de categorias e serviços com busca em largura (BFS), retornando caminhos relacionados à necessidade selecionada.

Para manter o problema de alocação limitado a um tamanho didático, o planejador aceita até 12 tarefas e 8 familiares por cálculo.

## Integrantes

- 562573 — Victor Antonio Teixeira da Silva
- 566244 — Samuel de Oliveira da Silva
- 566074 — Cristian Belasco Arcanjo
- 562613 — Lucas Oliveira de Mendonca Almeida
- 562608 — Joao Lucas Ferreira dos Santos
