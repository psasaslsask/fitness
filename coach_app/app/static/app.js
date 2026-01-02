const statusEl = document.getElementById("status");
const form = document.getElementById("daily-form");
const submitBtn = document.getElementById("submit-btn");
const resetBtn = document.getElementById("reset-btn");
const profileDetails = document.getElementById("profile-details");
const logsList = document.getElementById("logs-list");
const refreshProfileBtn = document.getElementById("refresh-profile");
const refreshLogsBtn = document.getElementById("refresh-logs");

const fields = [
  "log_date",
  "weight",
  "activity",
  "hunger_level",
  "food_eaten",
  "planned_workout",
];

const profileLabels = {
  sex: "Sex",
  height: "Height",
  weight_range: "Weight range",
  goal: "Goal",
  training_style: "Training style",
  focus_areas: "Focus areas",
  gym_closures: "Gym closures",
  menstrual_cycle_notes: "Cycle notes",
  fueling_sensitivity: "Fueling sensitivity",
  reassurance_needs: "Reassurance needs",
};

function setStatus(message, tone = "info") {
  statusEl.textContent = message;
  statusEl.dataset.tone = tone;
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  resetBtn.disabled = isLoading;
  form.querySelectorAll("input, textarea").forEach((el) => {
    el.disabled = isLoading;
  });
  setStatus(isLoading ? "Submitting..." : "Idle");
}

function fillDateToday() {
  const today = new Date().toISOString().slice(0, 10);
  document.getElementById("log_date").value = today;
}

function clearPanels() {
  ["recommendation", "reasoning", "calorie_estimate", "next_steps"].forEach((id) => {
    const el = document.getElementById(id);
    el.textContent = "Awaiting input.";
    el.classList.add("placeholder");
  });
}

function renderResponse(data) {
  const mapping = {
    recommendation: data.recommendation,
    reasoning: data.reasoning,
    calorie_estimate: data.calorie_estimate,
    next_steps: data.next_steps,
  };

  Object.entries(mapping).forEach(([key, value]) => {
    const el = document.getElementById(key);
    if (el) {
      el.textContent = value || "No data";
      el.classList.remove("placeholder");
    }
  });
}

function renderProfile(profile) {
  profileDetails.innerHTML = "";
  profileDetails.classList.remove("placeholder");

  Object.entries(profileLabels).forEach(([key, label]) => {
    const row = document.createElement("div");
    row.className = "description-row";

    const dt = document.createElement("dt");
    dt.textContent = label;

    const dd = document.createElement("dd");
    dd.textContent = profile[key] || "—";

    row.appendChild(dt);
    row.appendChild(dd);
    profileDetails.appendChild(row);
  });
}

function renderLogs(logs) {
  logsList.classList.remove("placeholder");
  logsList.innerHTML = "";

  if (!logs.length) {
    logsList.textContent = "No history yet.";
    return;
  }

  logs.forEach((log) => {
    const item = document.createElement("div");
    item.className = "log-row";

    const date = document.createElement("div");
    date.className = "log-date";
    date.textContent = log.log_id ? `Entry #${log.log_id}` : "Entry";

    const summary = document.createElement("div");
    summary.className = "log-summary";
    summary.textContent = log.recommendation || "Recommendation unavailable";

    item.appendChild(date);
    item.appendChild(summary);
    logsList.appendChild(item);
  });
}

async function fetchProfile() {
  try {
    const response = await fetch("/profile");
    if (!response.ok) {
      throw new Error("Profile not available yet");
    }
    const data = await response.json();
    renderProfile(data);
    setStatus("Profile loaded");
  } catch (err) {
    console.error(err);
    profileDetails.innerHTML =
      '<div class="description-row"><dt>Profile</dt><dd>Could not load profile.</dd></div>';
    profileDetails.classList.add("placeholder");
    setStatus(err.message || "Failed to load profile", "error");
  }
}

async function fetchLogs() {
  try {
    const response = await fetch("/logs");
    if (!response.ok) {
      throw new Error("Logs not available yet");
    }
    const data = await response.json();
    renderLogs(data);
    setStatus("History refreshed");
  } catch (err) {
    console.error(err);
    logsList.textContent = "Could not load history.";
    logsList.classList.add("placeholder");
    setStatus(err.message || "Failed to load logs", "error");
  }
}

async function submitCoach(event) {
  event.preventDefault();
  setLoading(true);

  try {
    const payload = {};
    fields.forEach((name) => {
      const value = form.elements[name].value.trim();
      payload[name] = value !== "" ? value : null;
    });

    const response = await fetch("/coach", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `Request failed: ${response.status}`);
    }

    const data = await response.json();
    renderResponse(data);
    setStatus("Updated");
    fetchLogs();
  } catch (err) {
    console.error(err);
    setStatus(err.message || "Something went wrong", "error");
  } finally {
    setLoading(false);
  }
}

function resetForm() {
  form.reset();
  fillDateToday();
  clearPanels();
  setStatus("Idle");
}

form.addEventListener("submit", submitCoach);
resetBtn.addEventListener("click", resetForm);
refreshProfileBtn.addEventListener("click", fetchProfile);
refreshLogsBtn.addEventListener("click", fetchLogs);

fillDateToday();
clearPanels();
fetchProfile();
fetchLogs();
setStatus("Idle");
