const tbody = document.querySelector("#leads-body");
const feedback = document.querySelector("#dashboard-feedback");
const count = document.querySelector("#lead-count");
const filter = document.querySelector("#status-filter");
const refresh = document.querySelector("#refresh-button");

const statuses = ["New", "Contacted", "Booked", "Closed"];
let leads = [];

function showFeedback(message, isError = false) {
  feedback.textContent = message;
  feedback.className = isError ? "error" : "success";
}

function addCell(row, value, className = "") {
  const cell = document.createElement("td");
  cell.textContent = value;
  cell.className = className;
  row.appendChild(cell);
  return cell;
}

function renderLeads() {
  tbody.replaceChildren();

  const visible = leads.filter(
    (lead) => !filter.value || lead.status === filter.value
  );

  count.textContent =
    `${visible.length} shown · ${leads.length} total enquiries`;

  if (visible.length === 0) {
    const row = document.createElement("tr");
    const cell = addCell(row, "No enquiries match this view.");
    cell.colSpan = 7;
    const aiCell = document.createElement("td");
    aiCell.className = "ai-insights";

    if (lead.ai_analysis) {
      const analysis = lead.ai_analysis;

      const summary = document.createElement("p");
      summary.textContent = analysis.summary;
      aiCell.appendChild(summary);

      const details = [
        ["Start", analysis.start_preference],
        ["Contact mentioned", analysis.contact_method],
        ["Contact time", analysis.contact_time],
        [
          "Requests",
          (analysis.requested_information || []).join(", "),
        ],
      ];

      for (const [label, value] of details) {
        if (!value) continue;

        const line = document.createElement("p");
        line.textContent = `${label}: ${value}`;
        aiCell.appendChild(line);
      }

      if (analysis.needs_human_review) {
        const review = document.createElement("p");
        review.className = "error";
        review.textContent =
          `Review needed: ${analysis.review_reason || "Check original enquiry."}`;
        aiCell.appendChild(review);
      }
    } else {
      const analyseButton = document.createElement("button");
      analyseButton.type = "button";
      analyseButton.textContent = "Analyse enquiry";

      analyseButton.addEventListener("click", async () => {
        analyseButton.disabled = true;
        analyseButton.textContent = "Analysing…";

        try {
          const response = await fetch(`/leads/${lead.id}/analyse`, {
            method: "POST",
          });

          const data = await response.json();

          if (!response.ok) {
            throw new Error(data.detail || "Analysis failed.");
          }

          lead.ai_analysis = data.analysis;
          renderLeads();
          showFeedback(`AI analysis saved for enquiry #${lead.id}.`);
        } catch (error) {
          showFeedback(error.message || "Unable to analyse enquiry.", true);
        } finally {
          analyseButton.disabled = false;
          analyseButton.textContent = "Analyse enquiry";
        }
      });

      aiCell.appendChild(analyseButton);
    }

    row.appendChild(aiCell);
    tbody.appendChild(row);
    return;
  }

  for (const lead of visible) {
    const row = document.createElement("tr");

    addCell(row, `#${lead.id}`);

    const customer = addCell(row, lead.name);

    const preference = document.createElement("span");
    preference.className = "customer-email";
    preference.textContent =
    `Preferred: ${lead.preferred_contact || "email"}`;
    customer.appendChild(preference);

    if (lead.email) {
    const email = document.createElement("span");
    email.className = "customer-email";
    email.textContent = lead.email;
    customer.appendChild(email);
    }

    if (lead.phone) {
    const phone = document.createElement("span");
    phone.className = "customer-email";
    phone.textContent = lead.phone;
    customer.appendChild(phone);
    }

    if (
    lead.preferred_contact === "whatsapp" &&
    lead.whatsapp_consent &&
    /^\+[1-9]\d{7,14}$/.test(lead.phone || "")
    ) {
    const whatsapp = document.createElement("a");
    whatsapp.className = "whatsapp-link";

    const message =
        `Hello ${lead.name}, thanks for your enquiry about ${lead.course}. ` +
        "How can we help you?";

    whatsapp.href =
        `https://wa.me/${lead.phone.slice(1)}?text=${encodeURIComponent(message)}`;

    whatsapp.target = "_blank";
    whatsapp.rel = "noopener noreferrer";
    whatsapp.textContent = "Open WhatsApp";
    customer.appendChild(whatsapp);
    }

    addCell(row, lead.course);
    addCell(row, lead.message, "lead-message");

    const date = new Date(lead.created_at);
    addCell(
      row,
      Number.isNaN(date.getTime()) ? "Unknown" : date.toLocaleString()
    );

    const statusCell = document.createElement("td");
    const select = document.createElement("select");
    select.setAttribute("aria-label", `Status for enquiry ${lead.id}`);

    for (const status of statuses) {
      const option = document.createElement("option");
      option.value = status;
      option.textContent = status;
      select.appendChild(option);
    }

    select.value = lead.status;
    select.addEventListener("change", () => updateStatus(lead, select));

    statusCell.appendChild(select);
    row.appendChild(statusCell);
    const aiCell = document.createElement("td");
    aiCell.className = "ai-insights";

    if (lead.ai_analysis) {
      const analysis = lead.ai_analysis;

      const summary = document.createElement("p");
      summary.textContent = analysis.summary;
      aiCell.appendChild(summary);

      const details = [
        ["Start", analysis.start_preference],
        ["Contact mentioned", analysis.contact_method],
        ["Contact time", analysis.contact_time],
        [
          "Requests",
          (analysis.requested_information || []).join(", "),
        ],
      ];

      for (const [label, value] of details) {
        if (!value) continue;

        const line = document.createElement("p");
        line.textContent = `${label}: ${value}`;
        aiCell.appendChild(line);
      }

      if (analysis.needs_human_review) {
        const review = document.createElement("p");
        review.className = "error";
        review.textContent =
          `Review needed: ${analysis.review_reason || "Check original enquiry."}`;
        aiCell.appendChild(review);
      }
    } else {
      const analyseButton = document.createElement("button");
      analyseButton.type = "button";
      analyseButton.textContent = "Analyse enquiry";

      analyseButton.addEventListener("click", async () => {
        analyseButton.disabled = true;
        analyseButton.textContent = "Analysing…";

        try {
          const response = await fetch(`/leads/${lead.id}/analyse`, {
            method: "POST",
          });

          const data = await response.json();

          if (!response.ok) {
            throw new Error(data.detail || "Analysis failed.");
          }

          lead.ai_analysis = data.analysis;
          renderLeads();
          showFeedback(`AI analysis saved for enquiry #${lead.id}.`);
        } catch (error) {
          showFeedback(error.message || "Unable to analyse enquiry.", true);
        } finally {
          analyseButton.disabled = false;
          analyseButton.textContent = "Analyse enquiry";
        }
      });

      aiCell.appendChild(analyseButton);
    }

    row.appendChild(aiCell);
    tbody.appendChild(row);
  }
}

async function loadLeads() {
  refresh.disabled = true;
  showFeedback("Loading enquiries…");

  try {
    const response = await fetch("/leads");
    if (!response.ok) throw new Error("Unable to load enquiries.");

    const data = await response.json();
    if (!Array.isArray(data)) throw new Error("Unexpected server response.");

    leads = data;
    renderLeads();
    showFeedback("Enquiries refreshed.");
  } catch (error) {
    showFeedback(
      "Could not refresh enquiries. Any displayed records may be outdated.",
      true
    );
  } finally {
    refresh.disabled = false;
  }
}

async function updateStatus(lead, select) {
  const previousStatus = lead.status;
  const newStatus = select.value;

  select.disabled = true;

  try {
    const response = await fetch(`/leads/${lead.id}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });

    if (!response.ok) throw new Error("Status update failed.");

    lead.status = newStatus;
    showFeedback(`Enquiry #${lead.id} updated to ${newStatus}.`);
    renderLeads();
  } catch (error) {
    select.value = previousStatus;
    showFeedback(
      "Could not confirm the update. Refresh to check the saved status.",
      true
    );
  } finally {
    select.disabled = false;
  }
}

filter.addEventListener("change", renderLeads);
refresh.addEventListener("click", loadLeads);
loadLeads();