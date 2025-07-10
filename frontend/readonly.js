(function () {
  const params = new URLSearchParams(window.location.search);
  const isReadonly = params.get("readonly") === "true";

  if (!isReadonly) return;

  // 1. Disable all form inputs
  document.querySelectorAll("input, textarea, select, canvas").forEach(el => {
    el.setAttribute("readonly", true);
    el.setAttribute("disabled", true);
  });

  // 2. Hide all editor-specific UI
  document.querySelectorAll(".editor-only, .icon-btn, .readonly-hide").forEach(el => {
    el.style.display = "none";
  });

  // 3. Prevent form submission
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", e => e.preventDefault());
  });

  // 4. Optional: Add a visual cue
  document.body.classList.add("readonly-mode");
})();
