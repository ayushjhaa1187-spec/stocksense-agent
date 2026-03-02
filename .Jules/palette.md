## 2025-03-02 - Keyboard Accessibility Focus States
**Learning:** Native focus states were completely missing or unstyled in the single-page application due to over-zealous reset or lack of explicit definition, leaving keyboard users with no visual feedback.
**Action:** Implemented a global `:focus-visible` rule using `currentColor` for the outline. `currentColor` automatically adapts the outline color to the text context (e.g., white on dark backgrounds, dark on light backgrounds), ensuring consistent high contrast without complex variable overrides.
