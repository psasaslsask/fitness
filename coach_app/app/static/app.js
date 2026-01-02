const statusEl = document.getElementById("status");
const form = document.getElementById("daily-form");
const submitBtn = document.getElementById("submit-btn");
const resetBtn = document.getElementById("reset-btn");

const fields = [
  "log_date",
  "weight",
  "activity",
  "hunger_level",
  "food_eaten",
  "planned_workout",
];

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

fillDateToday();
clearPanels();
setStatus("Idle");
