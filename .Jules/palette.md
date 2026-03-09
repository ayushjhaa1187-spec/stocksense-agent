## 2026-03-09 - Focus State and A11y Polish
**Learning:** Found an accessibility issue pattern specific to this app's components, where decorative feature icons lack `aria-hidden` and keyboard focus states are invisible due to the gradient background.
**Action:** Applied `currentColor` to `:focus-visible` to ensure contrast against varying backgrounds, hid decorative icons from screen readers, and implemented a proper skip-to-content link pattern.
