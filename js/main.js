const navToggle = document.querySelector(".nav-toggle");
const siteMenu = document.querySelector(".site-nav");
const menuLinks = document.querySelectorAll(".site-nav a");
const currentYear = document.querySelector("#current-year");

if (currentYear) {
  currentYear.textContent = new Date().getFullYear();
}

if (navToggle && siteMenu) {
  navToggle.addEventListener("click", () => {
    const isOpen = siteMenu.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  menuLinks.forEach((link) => {
    link.addEventListener("click", () => {
      siteMenu.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  });

  document.addEventListener("click", (event) => {
    if (!siteMenu.contains(event.target) && !navToggle.contains(event.target)) {
      siteMenu.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
    }
  });
}
