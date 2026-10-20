const search = document.querySelector("#document-search");
const links = [...document.querySelectorAll("[data-document-link]")];
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

  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      event.preventDefault();
      search.focus();
    }
  });
}
