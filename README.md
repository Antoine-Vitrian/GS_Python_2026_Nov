# Elo — cuidado compartilhado

## Ficha da CitizenTech

- **Projeto:** Elo — cuidado compartilhado.
- **Desafio:** ajudar famílias a organizar o cuidado de pessoas idosas ou dependentes e evitar que as tarefas fiquem concentradas em uma só pessoa.
- **Público-alvo:** familiares e pessoas que participam da rede de cuidado.
- **Proposta:** um protótipo local para organizar tarefas e compromissos, apoiar uma divisão equilibrada do trabalho e indicar caminhos de busca por serviços de apoio.
- **Funcionalidades principais:** divisão de tarefas por disponibilidade e carga atual, agenda, registro de tarefas concluídas, questionário visual de bem-estar e busca de apoio por necessidade.
- **Dados:** os familiares, tarefas e compromissos apresentados são simulados pela equipe. Os serviços da rede são exemplos ilustrativos; não representam uma consulta a cadastros oficiais nem estão conectados a prestadores.

## Integrantes

- 562573 — Victor Antonio Teixeira da Silva
- 566244 — Samuel de Oliveira da Silva
- 566074 — Cristian Belasco Arcanjo
- 562613 — Lucas Oliveira de Mendonca Almeida
- 562608 — Joao Lucas Ferreira dos Santos

## Funcionalidades

- Visão geral com tarefas, agenda e participação da família.
- Distribuição de tarefas considerando duração, carga já assumida e disponibilidade semanal de cada familiar.
- Questionário visual de bem-estar e painel de impacto para acompanhar a colaboração.
- Busca de serviços de apoio por necessidade, usando uma rede modelada como grafo.
- Registro de tarefas concluídas, inclusão de novas tarefas e compromissos.
- Protótipos visuais de lembretes e integração com WhatsApp. Os serviços externos ainda não estão conectados.

## Executar

Requisitos: Python 3.10 ou superior. A aplicação usa somente a biblioteca padrão do Python, sem instalação de pacotes.

```powershell
python app.py
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000) no navegador. Encerre o servidor com `Ctrl+C`.

## Onde estão as partes do trabalho

- **Memoização e tabulação:** `app.py`, nas funções `distribuir_com_memoizacao` e `distribuir_com_tabulacao`.
- **Grafo e busca de apoio:** `app.py`, nas estruturas `GRAFO_APOIO` e `SERVICOS_APOIO` e na função `buscar_caminhos_de_apoio`.
- **Interface:** `web/index.html` estrutura as telas, `web/styles.css` define o visual e `web/app.js` cuida das interações.
- **Prompts de IA:** registrados em [prompts.md](prompts.md).

O navegador se comunica com o servidor Python por três rotas locais: `/api/overview` carrega os dados, `/api/allocate` calcula a divisão das tarefas e `/api/support` busca serviços na rede de apoio. Os nomes dos campos JSON, como `members` e `tasks`, são mantidos em inglês para corresponder ao formato que a interface envia e recebe. Os métodos `do_GET` e `do_POST` também ficam com esses nomes porque fazem parte da interface padrão da biblioteca HTTP do Python.

## Algoritmos e análise de eficiência

O distribuidor valida os dados e a capacidade disponível antes de calcular. Seu objetivo é minimizar a maior proporção de tempo comprometido entre os familiares; em caso de empate, usa a soma dos quadrados dessas proporções como critério secundário.

- **Memoização:** `distribuir_com_memoizacao` resolve recursivamente estados definidos pelo índice do familiar e pela máscara das tarefas restantes. `functools.lru_cache` guarda os resultados já calculados para reutilizá-los.
- **Tabulação:** `distribuir_com_tabulacao` constrói iterativamente um dicionário de estados, indexado pela máscara das tarefas já atribuídas, mantendo a melhor pontuação encontrada.
- **Grafos:** `buscar_caminhos_de_apoio` percorre categorias e serviços com busca em largura (BFS), evitando revisitar nós. A fila usa `collections.deque` e `popleft()`, cuja retirada tem custo O(1), em vez de `list.pop(0)`.

Na análise, sejam **T** o número de tarefas e **M** o número de familiares. A geração dos subconjuntos possíveis custa O(M · T · 2^T). Em cada etapa da programação dinâmica, são considerados no máximo O(3^T) pares de estados e subconjuntos compatíveis. Como cada transição também copia o plano, com até M atribuições, o limite superior de tempo para cada estratégia é O(M² · 3^T). O espaço da memoização é O(M² · 2^T), considerando os estados armazenados e os planos guardados neles; na tabulação, que mantém apenas uma camada de estados por vez, é O(M · 2^T). A busca em largura custa O(V + E), em que V é o número de nós e E o número de arestas do grafo.

Para manter o cálculo limitado a um tamanho didático, a aplicação aceita até 12 tarefas e 8 familiares. Os dados simulados do projeto também permitem comparar os resultados das estratégias sem usar informações pessoais reais. A busca em largura retorna os serviços alcançáveis associados à necessidade selecionada.
