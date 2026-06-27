
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".mobile-toggle");
  const nav = document.querySelector(".nav-links");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      nav.style.display = nav.style.display === "flex" ? "none" : "flex";
      nav.style.position = "absolute";
      nav.style.top = "82px";
      nav.style.left = "0";
      nav.style.right = "0";
      nav.style.background = "#fff";
      nav.style.padding = "20px";
      nav.style.flexDirection = "column";
      nav.style.boxShadow = "0 20px 40px rgba(0,0,0,.1)";
    });
  }

  document.querySelectorAll("[data-filter]").forEach(tab => {
    tab.addEventListener("click", () => {
      const group = tab.closest(".tabs");
      group?.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
    });
  });
});
