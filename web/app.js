const state = {
  team: [],
  tasks: [],
  events: [],
  allocation: null,
  completed: new Set(),
  wellbeing: 3,
  selectedNeed: "saude",
  taskModal: null,
  simpleModal: null,
  toastTimer: null,
};

const icons = { Saúde: "✚", Rotina: "◷", Casa: "⌂", "Bem-estar": "☼", Afeto: "♡" };
const supportIcons = { "Saúde pública": "✚", Medicamentos: "＋", "Apoio e descanso": "☼", "Apoio familiar": "♡", "Orientação social": "✳", Direitos: "⚖", Comunidade: "⌂", "ONG comunitária": "♡" };
const viewNames = { inicio: "Visão geral", tarefas: "Tarefas", agenda: "Agenda", rede: "Rede de apoio", impacto: "Nosso impacto" };

async function request(url, options) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || "Não foi possível concluir agora.");
  return body;
}

function initials(name) {
  return name.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

function assignedMember(taskId) {
  if (!state.allocation) return null;
  return state.allocation.assignments.find((person) => person.tasks.some((task) => task.id === taskId));
}

function renderFamily() {
  const list = document.querySelector("#family-list");
  const people = state.allocation?.assignments || state.team.map((person) => ({ ...person, assignedMinutes: person.load, totalMinutes: person.load }));
  list.innerHTML = people.map((person) => {
    const percent = person.loadPercent ?? Math.round(person.totalMinutes / (person.availability * 60) * 100);
    return `<div class="family-row">
      <span class="person-avatar" style="background:${person.color}">${person.initials || initials(person.name)}</span>
      <span class="person-info"><strong>${person.name}</strong><small>${person.role || "Familiar"} · ${person.tasks?.length || 0} ${person.tasks?.length === 1 ? "tarefa" : "tarefas"}</small></span>
      <span class="person-hours"><strong>${(person.assignedMinutes / 60).toFixed(1)}h</strong>esta semana</span>
      <span class="family-progress"><span style="width:${Math.min(percent, 100)}%;background:${person.color}"></span></span>
    </div>`;
  }).join("");
}

function renderToday() {
  const timeline = document.querySelector("#today-timeline");
  const todayEvents = state.events.slice(0, 3);
  timeline.innerHTML = todayEvents.map((event) => `<div class="timeline-item">
    <span class="timeline-time">${event.time}</span><span class="timeline-track"><i class="timeline-dot ${event.color || ""}"></i></span>
    <span class="timeline-task"><strong>${event.title}</strong><small>${event.kind}</small></span><span class="timeline-owner">${event.owner}</span>
  </div>`).join("");
}

function renderTasks() {
  const board = document.querySelector("#task-board");
  board.innerHTML = state.tasks.map((task) => {
    const person = assignedMember(task.id);
    const done = state.completed.has(task.id);
    const categoryClass = task.category.toLowerCase().replaceAll(" ", "-");
    return `<article class="task-row ${done ? "task-completed" : ""}">
      <span class="task-type ${categoryClass}">${icons[task.category] || "♡"}</span>
      <span class="task-copy"><strong>${task.title}</strong><small>${task.detail || task.category}</small></span>
      <span class="task-meta"><span>◷</span>${task.minutes < 60 ? `${task.minutes} min` : `${Math.floor(task.minutes / 60)}h${task.minutes % 60 ? ` ${task.minutes % 60}m` : ""}`}</span>
      <span class="task-assignee">${person ? `<i class="person-avatar" style="background:${person.color}">${person.initials || initials(person.name)}</i>${person.name.split(" ")[0]}` : `<i class="person-avatar" style="background:#b7bfd8">?</i>A combinar`}</span>
      <button class="task-check ${done ? "done" : ""}" data-complete="${task.id}" aria-label="${done ? "Desmarcar" : "Marcar"} ${task.title}">${done ? "✓" : ""}</button>
    </article>`;
  }).join("");
  document.querySelector("#task-count-label").textContent = `${state.tasks.length} momentos de cuidado, compartilhados com carinho.`;
  document.querySelector("#nav-task-count").textContent = state.tasks.filter((task) => !state.completed.has(task.id)).length;
  renderWorkload();
}

function renderWorkload() {
  const container = document.querySelector("#workload-grid");
  const people = state.allocation?.assignments || state.team.map((person) => ({ ...person, assignedMinutes: 0, totalMinutes: person.load }));
  container.innerHTML = people.map((person) => {
    const used = person.totalMinutes;
    const capacity = person.availability * 60;
    const percent = Math.min(Math.round(used / capacity * 100), 100);
    return `<article class="workload-card">
      <div class="workload-top"><i class="person-avatar" style="background:${person.color}">${person.initials || initials(person.name)}</i><span><strong>${person.name}</strong><small>${person.role || "Familiar"}</small></span></div>
      <div class="load-labels"><span>Tempo combinado</span><b>${(used / 60).toFixed(1)}h / ${person.availability}h</b></div>
      <div class="load-meter"><span class="${percent >= 85 ? "high" : ""}" style="width:${percent}%;background:${percent >= 85 ? "" : person.color}"></span></div>
      <p class="load-note">${percent >= 85 ? "Carga alta · vale redistribuir" : `${person.tasks?.length || 0} tarefa${person.tasks?.length === 1 ? "" : "s"} nesta semana`}</p>
    </article>`;
  }).join("");
}

function renderEvents() {
  document.querySelector("#event-list").innerHTML = state.events.map((event) => `<article class="event-item">
    <span class="event-time">${event.time}</span><i class="event-color ${event.color || ""}"></i>
    <span class="event-copy"><strong>${event.title}</strong><small>${event.kind}</small></span><span class="event-owner">${event.owner}</span>
  </article>`).join("");
}

function renderCalendar() {
  const today = new Date();
  const monday = new Date(today);
  monday.setDate(today.getDate() - ((today.getDay() + 6) % 7));
  const weekdayNames = ["DOMINGO", "SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA", "SÁBADO"];
  document.querySelector("#calendar-month").innerHTML = `${new Intl.DateTimeFormat("pt-BR", { month: "long" }).format(today)} <span>${today.getFullYear()}</span>`;
  document.querySelector("#calendar-week").innerHTML = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(monday);
    date.setDate(monday.getDate() + index);
    const weekday = date.toLocaleDateString("pt-BR", { weekday: "short" }).replace(".", "").toUpperCase();
    return `<span class="${date.toDateString() === today.toDateString() ? "selected-day" : ""}"><small>${weekday}</small><b>${date.getDate()}</b></span>`;
  }).join("");
  document.querySelector("#calendar-day-name").textContent = weekdayNames[today.getDay()];
  document.querySelector("#calendar-day-date").textContent = new Intl.DateTimeFormat("pt-BR", { day: "numeric", month: "long" }).format(today);
  document.querySelector("#dashboard-date").textContent = new Intl.DateTimeFormat("pt-BR", { weekday: "long", day: "numeric", month: "long" }).format(today).toUpperCase();
  document.querySelector("#dashboard-today").textContent = new Intl.DateTimeFormat("pt-BR", { weekday: "long", day: "numeric", month: "long" }).format(today);
}

function renderImpact() {
  document.querySelector("#shared-count").textContent = 18 + state.completed.size;
  document.querySelector("#impact-count").textContent = 72 + state.completed.size;
}

function updateWellbeing(score) {
  state.wellbeing = score;
  document.querySelectorAll("[data-mood]").forEach((button) => {
    const selected = Number(button.dataset.mood) === score;
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  const status = score <= 2 ? "Preciso de apoio" : score === 3 ? "Um passo de cada vez" : score === 4 ? "Bem" : "Muito bem";
  document.querySelector("#wellbeing-status").textContent = status;
  showToast(score <= 2
    ? "Obrigada por contar. Vamos pensar em uma divisão mais leve para você."
    : "Obrigada por compartilhar como você está. ♡");
}

async function showSupport(need = state.selectedNeed) {
  state.selectedNeed = need;
  document.querySelectorAll(".need-card").forEach((card) => card.classList.toggle("selected", card.dataset.need === need));
  const result = await request(`/api/support?need=${encodeURIComponent(need)}`);
  document.querySelector("#support-count").textContent = `${result.results.length} caminhos`;
  document.querySelector("#support-results").innerHTML = result.results.map((place) => `<article class="support-card">
    <div class="support-card-top"><span class="support-card-icon">${supportIcons[place.type] || "♡"}</span><span class="support-card-tag">${place.tag}</span></div>
    <h3>${place.name}</h3><p>${place.description}</p>
    <div class="support-path">Caminho na rede: <span>${place.path.slice(1).map((node) => ({ saude: "Saúde", descanso: "Descanso", orientacao: "Orientação", convivencia: "Comunidade" }[node] || place.name).replaceAll("_", " ")).join(" → ")}</span></div>
  </article>`).join("");
}

function switchView(view) {
  if (!viewNames[view]) return;
  document.querySelectorAll(".view-panel").forEach((panel) => panel.classList.toggle("active", panel.id === `view-${view}`));
  document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === view));
  document.querySelector("#current-crumb").textContent = viewNames[view];
  if (view === "rede") showSupport().catch(showError);
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("visible");
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => toast.classList.remove("visible"), 2800);
}

function showError(error) {
  showToast(error.message || "Algo deu errado. Tente novamente.");
}

async function allocate(event) {
  const button = event.currentTarget;
  const original = button.innerHTML;
  button.disabled = true;
  button.innerHTML = "<span>✦</span> Pensando em vocês…";
  try {
    state.allocation = await request("/api/allocate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ team: state.team, members: state.team, tasks: state.tasks, algorithm: document.querySelector("#algorithm-select").value }),
    });
    renderTasks();
    renderFamily();
    const algorithm = state.allocation.algorithm === "tabulacao" ? "tabulação" : "memoização";
    showToast(`Prontinho! As tarefas foram organizadas com ${algorithm}.`);
  } catch (error) {
    showError(error);
  } finally {
    button.disabled = false;
    button.innerHTML = original;
  }
}

function openSimple(title, copy) {
  document.querySelector("#simple-modal-title").textContent = title;
  document.querySelector("#simple-modal-copy").textContent = copy;
  state.simpleModal.showModal();
}

function addTask(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const data = new FormData(form);
  const title = String(data.get("title")).trim();
  if (!title) return;
  state.tasks.push({
    id: `nova-${Date.now()}`, title, detail: "Tarefa adicionada pela família",
    minutes: Number(data.get("minutes")), category: String(data.get("category")), day: "A combinar",
  });
  state.allocation = null;
  renderTasks();
  renderFamily();
  renderToday();
  form.reset();
  state.taskModal.close();
  showToast("Tarefa adicionada. Vamos encontrar alguém para dividir.");
}

function markTask(taskId) {
  if (state.completed.has(taskId)) state.completed.delete(taskId);
  else state.completed.add(taskId);
  renderTasks();
  renderImpact();
  showToast(state.completed.has(taskId) ? "Tarefa marcada como concluída. Muito bem! ♡" : "Tudo bem, tarefa voltou para a lista.");
}

function openAddEvent() {
  const title = window.prompt("Qual compromisso vamos adicionar?");
  if (!title?.trim()) return;
  state.events.push({ time: "A combinar", title: title.trim(), kind: "Compromisso", owner: "A combinar", color: "mint" });
  renderEvents();
  renderToday();
  showToast("Compromisso adicionado à agenda da família.");
}

function bindEvents() {
  document.querySelectorAll(".nav-item").forEach((item) => item.addEventListener("click", () => switchView(item.dataset.view)));
  document.querySelectorAll("[data-view-link]").forEach((item) => item.addEventListener("click", () => switchView(item.dataset.viewLink)));
  document.querySelectorAll('[data-action="allocate"]').forEach((button) => button.addEventListener("click", allocate));
  document.querySelectorAll('[data-action="add-task"]').forEach((button) => button.addEventListener("click", () => state.taskModal.showModal()));
  document.querySelector('[data-action="invite"]').addEventListener("click", () => openSimple("Que bom que vocês estão aumentando a rede.", "Convide alguém importante para a família pelo botão de compartilhar. A conversa de vocês é um ótimo começo."));
  document.querySelector('[data-action="whatsapp"]').addEventListener("click", () => openSimple("Em breve, no WhatsApp também.", "Estamos preparando os lembretes e as confirmações de tarefas pelo WhatsApp para facilitar o dia a dia de todo mundo."));
  document.querySelector('[data-action="share-impact"]').addEventListener("click", () => openSimple("O cuidado que vocês compartilham inspira.", "Compartilhe esta conquista com a família. O importante é lembrar que cada gesto faz diferença."));
  document.querySelector('[data-action="mark-reminder"]').addEventListener("click", (event) => { event.currentTarget.textContent = "Lembrete anotado ✓"; showToast("Lembrete anotado com carinho."); });
  document.querySelector(".mood-dots").addEventListener("click", (event) => {
    const button = event.target.closest("[data-mood]");
    if (button) updateWellbeing(Number(button.dataset.mood));
  });
  document.querySelector('[data-action="add-event"]').addEventListener("click", openAddEvent);
  document.querySelector('[data-action="close-simple"]').addEventListener("click", () => state.simpleModal.close());
  document.querySelector("#task-form").addEventListener("submit", addTask);
  document.querySelector("#task-modal .modal-close").addEventListener("click", () => state.taskModal.close());
  document.querySelector("#simple-modal .modal-close").addEventListener("click", () => state.simpleModal.close());
  document.querySelector("#task-board").addEventListener("click", (event) => {
    const button = event.target.closest("[data-complete]");
    if (button) markTask(button.dataset.complete);
  });
  document.querySelector("#needs-grid").addEventListener("click", (event) => {
    const card = event.target.closest("[data-need]");
    if (card) showSupport(card.dataset.need).catch(showError);
  });
  document.querySelector(".calendar-controls").addEventListener("click", () => showToast("Sua agenda está mostrando esta semana."));
  document.querySelector("#today-label").textContent = new Intl.DateTimeFormat("pt-BR", { day: "numeric", month: "short" }).format(new Date());
  renderCalendar();
}

async function init() {
  state.taskModal = document.querySelector("#task-modal");
  state.simpleModal = document.querySelector("#simple-modal");
  bindEvents();
  try {
    const data = await request("/api/overview");
    state.team = data.team;
    state.tasks = data.tasks;
    state.events = data.events;
    renderFamily();
    renderToday();
    renderTasks();
    renderEvents();
    renderImpact();
  } catch (error) {
    showError(error);
  }
}

init();
