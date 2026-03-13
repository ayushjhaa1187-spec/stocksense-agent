
## 2026-03-13 - [A11y] Adaptive Focus Outlines & Hiding Decorative Elements
**Learning:** Hardcoding focus outline colors often leads to low contrast against varied backgrounds, failing accessibility guidelines. Screen readers redundantly announce decorative emojis, confusing users when adjacent text already provides the necessary context.
**Action:** Use `currentColor` for `:focus-visible` outlines (e.g., `outline: 3px solid currentColor;`) to ensure the outline dynamically adapts to the element's text color and maintains high contrast. Add `aria-hidden="true"` to purely decorative emojis to hide them from the accessibility tree while keeping them visually present.
