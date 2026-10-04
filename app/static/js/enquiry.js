const form = document.querySelector("#enquiry-form");
const button = document.querySelector("#submit-button");
const feedback = document.querySelector("#form-feedback");
const contactMethod = document.querySelector("#preferred_contact");
const phoneInput = document.querySelector("#phone");
const emailInput = document.querySelector("#email");
const consentInput = document.querySelector("#whatsapp_consent");

function updateContactFields() {
  const usesPhone = contactMethod.value !== "email";
  const usesWhatsApp = contactMethod.value === "whatsapp";

  document.querySelector("#phone-fields").hidden = !usesPhone;
  phoneInput.required = usesPhone;
  phoneInput.disabled = !usesPhone;

  emailInput.required = !usesPhone;
  document.querySelector("#email-optional").hidden = !usesPhone;

  document.querySelector("#whatsapp-permission").hidden = !usesWhatsApp;
  consentInput.required = usesWhatsApp;
  consentInput.disabled = !usesWhatsApp;

  if (!usesWhatsApp) consentInput.checked = false;
}

contactMethod.addEventListener("change", updateContactFields);
updateContactFields();
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (button.disabled) return;
    
  const fields = new FormData(form);

    const payload = {
    name: String(fields.get("name") ?? "").trim(),
    email: String(fields.get("email") ?? "").trim() || null,
    phone: String(fields.get("phone") ?? "").trim() || null,
    preferred_contact: contactMethod.value,
    whatsapp_consent:
        contactMethod.value === "whatsapp" && consentInput.checked,
    course: String(fields.get("course") ?? "").trim(),
    message: String(fields.get("message") ?? "").trim(),
    };

  button.disabled = true;
  button.textContent = "Sending…";
  feedback.textContent = "";
  feedback.className = "";

  try {
    const response = await fetch("/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      let message = "Unable to submit your enquiry. Please try again later.";

      if (response.status === 422 && Array.isArray(data.detail)) {
        message = data.detail
          .map((error) => `${error.loc.at(-1)}: ${error.msg}`)
          .join(" • ");
      }

      throw new Error(message);
    }

    document.querySelector("#thank-you-message").textContent =
    `We've received your interest in ${payload.course}.`;

    document.querySelector("#enquiry-reference").textContent =
    `Your reference number: #${data.lead_id}`;

    form.reset();
    updateContactFields();
    form.hidden = true;
    document.querySelector("#thank-you").hidden = false;
    document.querySelector("#thank-you-title").focus();
  } catch (error) {
    feedback.className = "error";
    feedback.textContent = error instanceof TypeError
      ? "We couldn’t confirm submission. Please check your connection."
      : error.message;
  } finally {
    button.disabled = false;
    button.textContent = "Send enquiry";
  }
});
document.querySelector("#another-enquiry").addEventListener("click", () => {
  document.querySelector("#thank-you").hidden = true;
  form.hidden = false;
  feedback.textContent = "";
  feedback.className = "";
  document.querySelector("#name").focus();
});