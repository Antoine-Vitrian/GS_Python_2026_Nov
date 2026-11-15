# Elo — cuidado compartilhado

Este documento reúne a proposta CitizenTech do projeto e sua relação com as
disciplinas da equipe. A aplicação é um protótipo acadêmico; os dados exibidos
são simulados.

## Ficha da proposta

- **Nome:** Elo — cuidado compartilhado.
- **Cidade e bairro:** a definir pela equipe.
- **Cidadão beneficiado:** pessoas idosas ou dependentes e seus familiares e
  cuidadores.
- **Problema, em uma frase:** a organização do cuidado pode sobrecarregar um
  único familiar e dificultar o acompanhamento de tarefas, compromissos e
  serviços de apoio.
- **Como funciona:** a plataforma organiza tarefas e compromissos, sugere uma
  divisão de tarefas considerando disponibilidade e carga atual, permite
  acompanhar o bem-estar e apresenta caminhos ilustrativos para encontrar
  serviços de apoio.
- **O que cada parte faz:** a interface apresenta a rotina e permite interagir
  com tarefas, agenda e busca de apoio; a aplicação Python fornece os dados,
  calcula a distribuição e percorre um grafo de serviços.
- **Link do repositório:** a preencher.
- **Indicador de impacto:** acompanhar a distribuição das tarefas entre os
  familiares, a participação de cada pessoa e as respostas de bem-estar ao
  longo do tempo. No protótipo, esses dados são demonstrativos e não comprovam
  impacto real.
- **ODS conectados:** ODS 3 — Saúde e Bem-Estar; ODS 10 — Redução das
  Desigualdades; ODS 11 — Cidades e Comunidades Sustentáveis.

## As seis perguntas da proposta

1. **Quem é o cidadão beneficiado?** Pessoas idosas ou dependentes, cuidadores
   e familiares que participam da organização do cuidado.
2. **Qual problema será resolvido?** A sobrecarga de cuidadores e a dificuldade
   de coordenar responsabilidades, compromissos e acesso à rede de apoio.
3. **Como a solução funcionará?** Uma agenda e lista de tarefas compartilhadas
   ajudam a família a planejar o cuidado. Um algoritmo sugere a distribuição
   das tarefas, e uma busca em grafo apresenta opções de apoio relacionadas à
   necessidade selecionada.
4. **Quais tecnologias serão empregadas?** Python e biblioteca padrão no
   servidor local; HTML, CSS e JavaScript na interface; programação dinâmica
   com memoização e tabulação para distribuir tarefas; e busca em largura
   (BFS) em um grafo para encontrar serviços de apoio.
5. **Quem participará do ecossistema?** A pessoa cuidada, familiares,
   cuidadores, serviços públicos, organizações comunitárias e profissionais
   que possam orientar a família. Os serviços mostrados hoje são exemplos,
   não uma consulta a cadastros oficiais.
6. **Como o impacto poderá ser medido e ampliado?** Podem ser acompanhados a
   participação dos familiares, o equilíbrio da carga de tarefas, o uso da
   agenda e a evolução das respostas de bem-estar. Uma avaliação real exigiria
   testes com usuários, consentimento e proteção de dados; a expansão poderia
   incluir cadastros locais verificados e integração com serviços parceiros.

## Percurso da equipe

1. **Observar:** escolher uma situação real relacionada à organização do
   cuidado e registrar o problema sem expor dados pessoais.
2. **Escutar:** conversar com pessoas que vivenciam essa rotina e entender o
   que já fazem, o que funciona e onde encontram dificuldades.
3. **Definir:** resumir o cidadão e o problema em uma frase que oriente as
   decisões do projeto.
4. **Rabiscar:** desenhar telas, fluxo de dados e funcionamento do algoritmo
   antes de implementar.
5. **Construir:** dividir o trabalho em interface, lógica de distribuição,
   agenda e rede de apoio, integrando as partes da equipe.
6. **Contar:** apresentar o problema, a solução funcionando, as tecnologias e
   quem ela pretende ajudar; separar claramente o que já existe do que é
   proposta futura.

Começar pequeno: uma solução simples que funciona vale mais do que uma ideia
grande pela metade.

## Relação com as disciplinas

As disciplinas abaixo foram transcritas da imagem compartilhada. O primeiro
nome aparece truncado na imagem; confirme o título completo com a equipe.

| Disciplina ou canal visível | Relação com o projeto |
| --- | --- |
| Agile Methodology with Squad Fra... | Organizar o trabalho em etapas, dividir tarefas entre integrantes e integrar entregas. O título aparece incompleto na imagem. |
| AR VR Modelling and Simulation | Pode apoiar uma exploração futura de simulação ou visualização; não é uma tecnologia implementada no protótipo atual. |
| Data Science e Statistical Computing | Definir e interpretar indicadores de participação, carga de tarefas e bem-estar, sem tirar conclusões de impacto real a partir de dados simulados. |
| Database Design | Planejar como pessoas, tarefas, compromissos e serviços poderiam ser persistidos. O protótipo atual usa dados simulados na aplicação, sem banco de dados conectado. |
| Dynamic Programming | Implementar e comparar as estratégias de memoização e tabulação para distribuir tarefas respeitando disponibilidade e carga dos familiares. |
| Network Architect Solutions | Pensar na comunicação entre interface e servidor e em futuras integrações com serviços externos; essas integrações ainda não estão conectadas. |
| Domain Driven Design – Java | Identificar conceitos do domínio do cuidado e seus relacionamentos. A aplicação existente está implementada em Python, não em Java. |

Na imagem também aparece **“Grupo 6 - 200 por cento JAVA”**, que parece ser
um canal de grupo, e não uma disciplina. Foi mantido separado da lista de
disciplinas para não classificar o canal incorretamente.

## Limites atuais do protótipo

- A aplicação usa dados demonstrativos; não deve receber informações reais de
  saúde ou dados pessoais.
- Os serviços de apoio são ilustrativos e não representam disponibilidade,
  elegibilidade ou vínculo com instituições reais.
- Lembretes e integração com WhatsApp são protótipos visuais, sem conexão com
  serviços externos.
- A divisão sugerida é um apoio ao planejamento familiar, não uma avaliação
  profissional nem uma substituição do diálogo entre as pessoas envolvidas.
