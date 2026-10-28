window.MathJax = {
  loader: {load: ["a11y/assistive-mml", "a11y/semantic-enrich", "a11y/explorer"]},
  tex: {inlineMath: [["\\(", "\\)"]], displayMath: [["\\[", "\\]"]], processEscapes: true},
  options: {ignoreHtmlClass: ".*|", processHtmlClass: "arithmatex", enableMenu: true,
    enableAssistiveMml: true, enableEnrichment: true},
  svg: {fontCache: "local"}
};
