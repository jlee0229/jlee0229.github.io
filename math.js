// Renders the TeX that build.py leaves in <span class="math"> and <div class="math display">.
// Loaded only on pages that have math, after KaTeX.
(function () {
  function run() {
    if (!window.katex) return;
    document.querySelectorAll(".math").forEach(function (el) {
      try {
        katex.render(el.textContent, el, {
          displayMode: el.classList.contains("display"),
          throwOnError: false,
          output: "htmlAndMathml",
        });
      } catch (e) { /* leave the TeX visible */ }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();
