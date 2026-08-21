const navToggle = document.querySelector(".nav-toggle");
const siteMenu = document.querySelector(".site-nav");
const menuLinks = document.querySelectorAll(".site-nav a");
const currentYear = document.querySelector("#current-year");
const contactForm = document.querySelector("#contact-form");

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

if (contactForm) {
  contactForm.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!contactForm.reportValidity()) {
      return;
    }

    const formData = new FormData(contactForm);
    const nombre = formData.get("nombre") || "";
    const empresa = formData.get("empresa") || "";
    const email = formData.get("email") || "";
    const servicio = formData.get("servicio") || "";
    const mensaje = formData.get("mensaje") || "";
    const subject = encodeURIComponent(`Consulta web Efmarco - ${servicio}`);
    const body = encodeURIComponent(
      [
        `Nombre: ${nombre}`,
        `Empresa o institución: ${empresa}`,
        `Email: ${email}`,
        `Servicio de interés: ${servicio}`,
        "",
        "Mensaje:",
        mensaje,
      ].join("\n")
    );
    const mailtoUrl = `mailto:info@efmarco.com.ar?subject=${subject}&body=${body}`;

    if (mailtoUrl.length > 2000) {
      window.alert("El mensaje es demasiado largo para enviarlo desde el navegador. Por favor resumilo o escribinos directamente a info@efmarco.com.ar.");
      return;
    }

    window.location.href = mailtoUrl;
  });
}
