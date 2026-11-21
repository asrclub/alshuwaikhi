/* AlShuwaikhi sharing: works on the public website and inside Android WebView. */
(() => {
  "use strict";
  const WEBSITE_URL = "https://alshuwaikhi.pages.dev/";
  const toggle = document.getElementById("shareToggle");
  const panel = document.getElementById("sharePopover");
  const feedback = document.getElementById("shareFeedback");
  if (!toggle || !panel || !feedback) return;

  let feedbackTimer;
  function showFeedback(message) {
    feedback.textContent = message;
    feedback.hidden = false;
    clearTimeout(feedbackTimer);
    feedbackTimer = setTimeout(() => { feedback.hidden = true; }, 3200);
  }

  function setOpen(open) {
    panel.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "إغلاق خيارات المشاركة" : "افتح أزرار مشاركة الموقع");
  }

  toggle.addEventListener("click", () => setOpen(panel.hidden));
  document.addEventListener("click", (event) => {
    if (!panel.hidden && !event.target.closest(".share-floating")) setOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });
  panel.querySelectorAll('a[href]').forEach((link) => link.addEventListener("click", () => setOpen(false)));

  async function copyUrl() {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(WEBSITE_URL);
        return true;
      } catch (_) { /* Use WebView-compatible fallback below. */ }
    }
    const field = document.createElement("textarea");
    field.value = WEBSITE_URL;
    field.setAttribute("readonly", "");
    field.style.cssText = "position:fixed;left:-9999px;top:0;opacity:0;";
    document.body.appendChild(field);
    field.focus();
    field.select();
    let success = false;
    try { success = document.execCommand("copy"); }
    catch (_) { /* Older WebViews can disallow copy. */ }
    field.remove();
    return success;
  }

  document.querySelectorAll("[data-copy-share]").forEach(button => {
    button.addEventListener("click", async () => {
      const copied = await copyUrl();
      showFeedback(copied ? "تم نسخ رابط الشويخي ✓" : "تعذر نسخ الرابط تلقائيًا. يمكنك نسخه من شريط العنوان.");
      if (copied) setOpen(false);
    });
  });
})();
