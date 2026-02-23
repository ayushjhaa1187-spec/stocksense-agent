# Palette's Journal - Critical UX Learnings

This journal documents critical UX and accessibility learnings.

Format:
## YYYY-MM-DD - [Title]
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

---

## 2026-02-23 - Semantic Wrappers vs Flex Layouts
**Learning:** Wrapping a flex item (like .hero) in a semantic tag (like <main>) breaks the layout if the wrapper doesn't inherit the flex properties.
**Action:** Always ensure the new semantic wrapper has flex: 1 and appropriate display properties (e.g., display: flex; flex-direction: column) to maintain the original layout behavior.
