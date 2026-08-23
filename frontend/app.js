const API = "/api";
let ALL_ROLES = [];
let SELECTED_ROLE_ID = null;

// ---------- Tabs ----------
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`view-${tab.dataset.view}`).classList.add("active");
  });
});

// ---------- Init ----------
async function init() {
  const res = await fetch(`${API}/roles`);
  ALL_ROLES = await res.json();
  renderRoleList(ALL_ROLES);
  populateCompareSelects();
  if (ALL_ROLES.length) selectRole(ALL_ROLES[0].id);
}

// ---------- Explorer ----------
function renderRoleList(roles) {
  const list = document.getElementById("roleList");
  list.innerHTML = "";
  roles.forEach(r => {
    const li = document.createElement("li");
    li.dataset.id = r.id;
    if (r.id === SELECTED_ROLE_ID) li.classList.add("selected");
    li.innerHTML = `
      <div class="rl-title">${r.title}</div>
      <div class="rl-level">${r.level} &middot; ${r.automation_pct + r.augmentation_pct}% AI exposure</div>
      <div class="mini-bar">
        <span class="seg-auto" style="width:${r.automation_pct}%"></span>
        <span class="seg-aug" style="width:${r.augmentation_pct}%"></span>
      </div>`;
    li.addEventListener("click", () => selectRole(r.id));
    list.appendChild(li);
  });
}

document.getElementById("roleSearch").addEventListener("input", (e) => {
  const q = e.target.value.toLowerCase();
  renderRoleList(ALL_ROLES.filter(r => r.title.toLowerCase().includes(q)));
});

async function selectRole(id) {
  SELECTED_ROLE_ID = id;
  document.querySelectorAll("#roleList li").forEach(li => {
    li.classList.toggle("selected", Number(li.dataset.id) === id);
  });
  const res = await fetch(`${API}/roles/${id}`);
  const role = await res.json();
  renderRoleDetail(role);
}

function classificationLabel(c) {
  return { automated: "Automated", augmented: "Augmented", "human-led": "Human-led" }[c] || c;
}

function renderRoleDetail(role) {
  const panel = document.getElementById("roleDetail");
  const activityRows = role.activities.map(a => `
    <div class="activity-row">
      <div class="ar-top">
        <span class="ar-name">${a.name}</span>
        <span class="ar-tag ${a.classification}">${classificationLabel(a.classification)}</span>
      </div>
      <div class="ar-weight">${a.weight}% of time &middot; automation ${a.automation_score}% &middot; augmentation ${a.augmentation_score}%</div>
      <div class="ar-reason">${a.reason}</div>
    </div>`).join("");

  panel.innerHTML = `
    <div class="rd-header">
      <div>
        <h2>${role.title}</h2>
        <div class="rd-processes">${role.processes.join(" &middot; ")}</div>
      </div>
      <span class="rd-level-badge">${role.level}</span>
    </div>

    <div class="impact-gauge">
      <div class="bar">
        <span class="seg-auto" style="width:${role.automation_pct}%">${role.automation_pct > 8 ? role.automation_pct + '%' : ''}</span>
        <span class="seg-aug" style="width:${role.augmentation_pct}%">${role.augmentation_pct > 8 ? role.augmentation_pct + '%' : ''}</span>
        <span class="seg-unaffected" style="width:${role.unaffected_pct}%">${role.unaffected_pct > 8 ? role.unaffected_pct + '%' : ''}</span>
      </div>
      <div class="impact-legend">
        <span><i class="dot" style="background:var(--gold)"></i>Automated ${role.automation_pct}%</span>
        <span><i class="dot" style="background:var(--teal)"></i>Augmented ${role.augmentation_pct}%</span>
        <span><i class="dot" style="background:#3a4552"></i>Unaffected ${role.unaffected_pct}%</span>
      </div>
      <span class="confidence-chip ${role.confidence}">confidence: ${role.confidence}</span>
    </div>

    <div class="rd-section">
      <h3>Future role profile</h3>
      <p class="rd-narrative">${role.future_role_profile}</p>
    </div>

    <div class="rd-section">
      <h3>Current skills</h3>
      <div class="chip-row">${role.current_skills.map(s => `<span class="chip">${s}</span>`).join("")}</div>
    </div>

    <div class="rd-section">
      <h3>Future skills</h3>
      <div class="chip-row">${role.future_skills.map(s => `<span class="chip">${s}</span>`).join("")}</div>
    </div>

    <div class="rd-section">
      <h3>New responsibilities</h3>
      <div class="chip-row">${role.new_responsibilities.map(s => `<span class="chip">${s}</span>`).join("")}</div>
    </div>

    <div class="rd-section">
      <h3>Activity-level breakdown &amp; explainability</h3>
      ${activityRows}
    </div>

    <div class="rd-section">
      <h3>AI exposure today</h3>
      <p class="rd-narrative">${role.ai_exposure_today}</p>
    </div>
  `;
}

// ---------- Compare ----------
function populateCompareSelects() {
  const a = document.getElementById("compareA");
  const b = document.getElementById("compareB");
  ALL_ROLES.forEach((r, i) => {
    a.innerHTML += `<option value="${r.title}" ${i === 0 ? "selected" : ""}>${r.title}</option>`;
    b.innerHTML += `<option value="${r.title}" ${i === 1 ? "selected" : ""}>${r.title}</option>`;
  });
}

document.getElementById("runCompare").addEventListener("click", async () => {
  const a = document.getElementById("compareA").value;
  const b = document.getElementById("compareB").value;
  const res = await fetch(`${API}/compare?role_a=${encodeURIComponent(a)}&role_b=${encodeURIComponent(b)}`);
  if (!res.ok) { document.getElementById("compareResult").innerHTML = "<p>Could not compare those roles.</p>"; return; }
  const data = await res.json();
  renderCompare(data);
});

function compareCard(role) {
  return `
    <div class="compare-card">
      <h3 style="font-family:var(--font-display);font-size:19px;margin:0 0 10px;">${role.title}</h3>
      <div class="impact-gauge">
        <div class="bar">
          <span class="seg-auto" style="width:${role.automation_pct}%"></span>
          <span class="seg-aug" style="width:${role.augmentation_pct}%"></span>
          <span class="seg-unaffected" style="width:${role.unaffected_pct}%"></span>
        </div>
        <div class="impact-legend">
          <span>Automated ${role.automation_pct}%</span>
          <span>Augmented ${role.augmentation_pct}%</span>
          <span>Unaffected ${role.unaffected_pct}%</span>
        </div>
      </div>
      <p class="rd-narrative" style="font-size:13.5px;">${role.future_role_profile}</p>
    </div>`;
}

function renderCompare(data) {
  document.getElementById("compareResult").innerHTML = `
    <div class="compare-grid">
      ${compareCard(data.role_a)}
      ${compareCard(data.role_b)}
    </div>
    <div class="compare-narrative">${data.narrative}</div>
  `;
}

// ---------- Rank ----------
document.getElementById("runRank").addEventListener("click", async () => {
  const n = document.getElementById("rankN").value || 5;
  const res = await fetch(`${API}/rank?n=${n}`);
  const data = await res.json();
  renderRank(data);
});

function renderRank(data) {
  const rows = data.top_roles.map((r, i) => `
    <div class="rank-row">
      <span class="rr-num">${String(i + 1).padStart(2, "0")}</span>
      <span class="rr-title">${r.title}</span>
      <div class="rr-bar">
        <span class="seg-auto" style="width:${r.automation_pct}%"></span>
        <span class="seg-aug" style="width:${r.augmentation_pct}%"></span>
      </div>
      <span class="rr-score">${r.change_score}%</span>
    </div>`).join("");
  document.getElementById("rankResult").innerHTML = `
    ${rows}
    <div class="compare-narrative">${data.narrative}</div>
  `;
}

init();
