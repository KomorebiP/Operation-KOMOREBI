"use strict";

// All examples are ordinary visible sections until enhancement succeeds.
// Selection is always manual: no timer, motion, or unexpected focus changes.
const showcase = document.querySelector(".home-showcase");
if (showcase) {
  const slides = Array.from(showcase.querySelectorAll(".home-slide"));
  const topics = showcase.querySelector(".home-topics");
  const tabs = Array.from(topics.querySelectorAll("button"));
  const controls = showcase.querySelector(".home-slide-controls");
  const position = showcase.querySelector(".home-slide-position");
  let current = 0;

  function select(index, focus = false) {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== current; });
    tabs.forEach((tab, i) => {
      tab.setAttribute("aria-selected", String(i === current));
      tab.tabIndex = i === current ? 0 : -1;
    });
    position.textContent = `${String(current + 1).padStart(2, "0")} / ${String(slides.length).padStart(2, "0")} · ${tabs[current].textContent}`;
    if (focus) tabs[current].focus();
  }

  if (slides.length > 1 && slides.length === tabs.length) {
    topics.setAttribute("role", "tablist");
    tabs.forEach((tab, i) => {
      tab.setAttribute("role", "tab");
      slides[i].setAttribute("role", "tabpanel");
      slides[i].setAttribute("aria-labelledby", tab.id);
      slides[i].tabIndex = 0;
      tab.addEventListener("click", () => select(i));
    });
    topics.addEventListener("keydown", event => {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      let next;
      if (event.key === "ArrowRight") next = current + 1;
      else if (event.key === "ArrowLeft") next = current - 1;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = slides.length - 1;
      else return;
      event.preventDefault();
      select(next, true);
    });
    showcase.querySelector("[data-slide-previous]").addEventListener("click", () => select(current - 1));
    showcase.querySelector("[data-slide-next]").addEventListener("click", () => select(current + 1));

    // Swipe only on noninteractive content, leaving links and vertical scroll alone.
    let start;
    const feature = showcase.querySelector(".home-feature");
    feature.addEventListener("pointerdown", event => {
      start = event.isPrimary && event.pointerType === "touch" && !event.target.closest("a,button")
        ? {x: event.clientX, y: event.clientY, id: event.pointerId} : null;
    });
    feature.addEventListener("pointercancel", () => { start = null; });
    feature.addEventListener("pointerup", event => {
      if (!start || event.pointerId !== start.id) return;
      const dx = event.clientX - start.x;
      const dy = event.clientY - start.y;
      start = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 2) select(current + (dx < 0 ? 1 : -1));
    });
    function linkedSlide() {
      let target;
      try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); }
      catch { return -1; }
      return target ? slides.findIndex(slide => slide.contains(target)) : -1;
    }
    const linked = linkedSlide();
    select(linked < 0 ? 0 : linked);
    window.addEventListener("hashchange", () => {
      const linked = linkedSlide();
      if (linked >= 0) select(linked);
    });
    topics.hidden = false;
    controls.hidden = false;
    showcase.classList.add("home-slides-ready");
  }
}
