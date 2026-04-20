function authHeaders() {
  const user = document.getElementById("xUser").value || "admin-demo";
  const role = document.getElementById("xRole").value || "admin";
  return { "X-User": user, "X-Role": role, "Content-Type": "application/json" };
}

async function apiGet(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function apiPost(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function cleanPayload(formData) {
  const data = Object.fromEntries(formData.entries());
  for (const key of Object.keys(data)) {
    if (data[key] === "") data[key] = null;
  }
  if (data.provider_id) data.provider_id = Number(data.provider_id);
  if (data.supply_id) data.supply_id = Number(data.supply_id);
  if (data.expediente_id) data.expediente_id = Number(data.expediente_id);
  return data;
}

function renderList(elId, items, mapper) {
  const el = document.getElementById(elId);
  el.innerHTML = "";
  for (const item of items) {
    const li = document.createElement("li");
    li.innerHTML = mapper(item);
    el.appendChild(li);
  }
}

async function refreshKpis() {
  const data = await apiGet("/dashboard/kpis");
  document.getElementById("kpiTotal").textContent = data.total_supplies;
  document.getElementById("kpiOpen").textContent = data.open_supplies;
  document.getElementById("kpiClosed").textContent = data.closed_supplies;
  document.getElementById("kpiOverdue").textContent = data.overdue_without_movement;
}

async function refreshProviders() {
  const providers = await apiGet("/providers");
  renderList("providerList", providers, (p) => `#${p.id} - <strong>${p.business_name}</strong> (${p.tax_id || "sin CUIT"})`);
}

async function refreshSupplies() {
  const supplies = await apiGet("/supplies");
  renderList(
    "supplyList",
    supplies,
    (s) => `#${s.id} - <strong>${s.title}</strong> | ${s.requester_dependency} | etapa: ${s.current_stage}`,
  );
}

async function refreshMemos() {
  const memos = await apiGet("/memos");
  renderList("memoList", memos, (m) => `#${m.id} - <strong>${m.number}</strong> | ${m.description}`);
}

async function refreshTasks() {
  const tasks = await apiGet("/tasks");
  renderList(
    "taskList",
    tasks,
    (t) => `#${t.id} - <strong>${t.title}</strong> | estado: ${t.status} ${t.supply_id ? `| sum:${t.supply_id}` : ""}`,
  );
}

function wireForm(formId, endpoint, afterRefresh) {
  const form = document.getElementById(formId);
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = cleanPayload(new FormData(form));
      await apiPost(endpoint, payload);
      form.reset();
      await afterRefresh();
      await refreshKpis();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  });
}

async function init() {
  document.getElementById("btnRefreshKpi").addEventListener("click", refreshKpis);

  wireForm("providerForm", "/providers", refreshProviders);
  wireForm("supplyForm", "/supplies", refreshSupplies);
  wireForm("memoForm", "/memos", refreshMemos);
  wireForm("taskForm", "/tasks", refreshTasks);

  await refreshKpis();
  await Promise.all([refreshProviders(), refreshSupplies(), refreshMemos(), refreshTasks()]);
}

init().catch((err) => alert(`No se pudo inicializar la app: ${err.message}`));
