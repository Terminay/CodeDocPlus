/* ─── Sidebar search filter ───────────────────────────────────────────────── */
const search = document.querySelector("#document-search");
const links  = [...document.querySelectorAll("[data-document-link]")];
const emptyState = document.querySelector(".search-empty");

if (search) {
  search.addEventListener("input", () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const link of links) {
      const matches = link.textContent.toLocaleLowerCase().includes(query);
      link.hidden = !matches;
      if (matches) visible += 1;
    }
    if (emptyState) emptyState.hidden = visible > 0 || query.length === 0;
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      e.preventDefault();
      search.focus();
    }
  });
}


/* ─── Mobile sidebar toggle ──────────────────────────────────────────────── */
const toggle   = document.getElementById("nav-toggle");
const sidebar  = document.getElementById("sidebar");
const backdrop = document.getElementById("sidebar-backdrop");

function openSidebar() {
  sidebar.classList.add("is-open");
  backdrop.classList.add("is-visible");
  backdrop.removeAttribute("hidden");
  toggle.setAttribute("aria-expanded", "true");
  document.body.style.overflow = "hidden";
}

function closeSidebar() {
  sidebar.classList.remove("is-open");
  backdrop.classList.remove("is-visible");
  toggle.setAttribute("aria-expanded", "false");
  document.body.style.overflow = "";
}

if (toggle && sidebar && backdrop) {
  toggle.addEventListener("click", () => {
    const isOpen = sidebar.classList.contains("is-open");
    isOpen ? closeSidebar() : openSidebar();
  });

  backdrop.addEventListener("click", closeSidebar);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sidebar.classList.contains("is-open")) closeSidebar();
  });
}


/* ─── Table-of-contents scroll-spy ──────────────────────────────────────── */
const tocLinks   = [...document.querySelectorAll("[data-toc-link]")];
const navbarH    = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--navbar-h") || "51", 10);

if (tocLinks.length > 0) {
  const headingIds = tocLinks.map(l => l.getAttribute("href").slice(1));
  const headings   = headingIds.map(id => document.getElementById(id)).filter(Boolean);

  let lastActive = null;

  function updateActiveLink() {
    const scrollY = window.scrollY + navbarH + 20;
    let current   = headings[0];

    for (const heading of headings) {
      if (heading.offsetTop <= scrollY) current = heading;
    }

    if (current && current.id !== lastActive) {
      lastActive = current.id;
      for (const link of tocLinks) {
        const isActive = link.getAttribute("href") === "#" + current.id;
        link.classList.toggle("is-active", isActive);
      }
    }
  }

  window.addEventListener("scroll", updateActiveLink, { passive: true });
  updateActiveLink();
}
