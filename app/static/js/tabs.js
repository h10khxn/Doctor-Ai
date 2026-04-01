(() => {
  function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const panelId = btn.getAttribute("aria-controls");
        if (!panelId) return;

        tabBtns.forEach(b => {
          b.classList.remove("active");
          b.setAttribute("aria-selected", "false");
        });
        document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));

        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
        const panel = document.getElementById(panelId);
        if (panel) panel.classList.add("active");
      });
    });
  }

  function initHamburger() {
    const btn = document.querySelector(".nav-hamburger");
    const links = document.querySelector(".nav-links");
    if (!btn || !links) return;
    btn.addEventListener("click", () => {
      const open = links.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initHamburger();
  });
})();
