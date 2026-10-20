import { useEffect, useState } from "react";

const STORAGE_KEY = "codedocplus-theme";

function resolvedTheme(pref) {
  if (pref === "light" || pref === "dark") return pref;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(pref) {
  const theme = resolvedTheme(pref);
  document.documentElement.setAttribute("data-theme", theme);
  document.documentElement.style.colorScheme = theme;
}

export function useTheme() {
  const [pref, setPref] = useState(() => localStorage.getItem(STORAGE_KEY) || "system");

  useEffect(() => {
    applyTheme(pref);
  }, [pref]);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if (localStorage.getItem(STORAGE_KEY) === null || localStorage.getItem(STORAGE_KEY) === "system") {
        applyTheme("system");
      }
    };
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  const cycle = () => {
    const order = ["system", "light", "dark"];
    const next = order[(order.indexOf(pref) + 1) % order.length];
    setPref(next);
    if (next === "system") localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, next);
  };

  const label = pref === "light" ? "Light" : pref === "dark" ? "Dark" : "System";
  return { pref, label, cycle };
}
