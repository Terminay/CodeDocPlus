(function () {
  "use strict";

  // ---------- Theme ----------

  var STORAGE_KEY = "codedocplus-theme";
  var root = document.documentElement;

  function resolvedTheme(preference) {
    if (preference === "light" || preference === "dark") return preference;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(preference) {
    root.setAttribute("data-theme", resolvedTheme(preference));
    root.style.colorScheme = resolvedTheme(preference);
  }

  function currentPreference() {
    return localStorage.getItem(STORAGE_KEY) || "system";
  }

  function setPreference(preference) {
    if (preference === "light" || preference === "dark" || preference === "system") {
      localStorage.setItem(STORAGE_KEY, preference);
    } else {
      preference = "system";
      localStorage.removeItem(STORAGE_KEY);
    }
    applyTheme(preference);
    syncToggleLabel(preference);
  }

  function syncToggleLabel(preference) {
    var toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) return;
    var label = toggle.querySelector(".toggle-label");
    if (!label) return;
    if (preference === "light") label.textContent = "Light";
    else if (preference === "dark") label.textContent = "Dark";
    else label.textContent = "System";
  }

  applyTheme(currentPreference());
  syncToggleLabel(currentPreference());

  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", function () {
      if (currentPreference() === "system") applyTheme("system");
    });

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) {
      toggle.addEventListener("click", function () {
        var order = ["system", "light", "dark"];
        var current = currentPreference();
        var next = order[(order.indexOf(current) + 1) % order.length];
        setPreference(next);
      });
    }
  });

  // ---------- Sidebar (mobile) ----------

  document.addEventListener("DOMContentLoaded", function () {
    var openBtn = document.querySelector("[data-sidebar-open]");
    var closeBtn = document.querySelector("[data-sidebar-close]");
    var sidebar = document.querySelector(".sidebar");
    var scrim = document.querySelector(".scrim");

    function open() {
      if (sidebar) sidebar.classList.add("is-open");
      if (scrim) scrim.classList.add("is-open");
    }
    function close() {
      if (sidebar) sidebar.classList.remove("is-open");
      if (scrim) scrim.classList.remove("is-open");
    }

    if (openBtn) openBtn.addEventListener("click", open);
    if (closeBtn) closeBtn.addEventListener("click", close);
    if (scrim) scrim.addEventListener("click", close);

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") close();
    });
  });

  // ---------- Search ----------

  document.addEventListener("DOMContentLoaded", function () {
    var search = document.querySelector("#document-search");
    var links = Array.prototype.slice.call(document.querySelectorAll("[data-document-link]"));
    var emptyState = document.querySelector(".search-empty");
    if (!search) return;

    search.addEventListener("input", function () {
      var query = search.value.trim().toLowerCase();
      var visible = 0;
      links.forEach(function (link) {
        var matches = link.textContent.toLowerCase().indexOf(query) !== -1;
        link.hidden = !matches;
        if (matches) visible += 1;
      });
      if (emptyState) emptyState.hidden = visible > 0 || query.length === 0;
    });

    document.addEventListener("keydown", function (event) {
      var tag = document.activeElement && document.activeElement.tagName;
      if (event.key === "/" && tag !== "INPUT" && tag !== "TEXTAREA") {
        event.preventDefault();
        search.focus();
      }
    });
  });
})();
