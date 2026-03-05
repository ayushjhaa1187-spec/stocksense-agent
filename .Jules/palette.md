## 2024-05-18 - currentColor for focus-visible outlines
**Learning:** Using `outline: 3px solid currentColor;` for `:focus-visible` automatically adapts the outline color to the text color, providing sufficient contrast across different background colors without needing to override focus styles for specific elements or sections.
**Action:** Use `currentColor` in global `:focus-visible` styles to handle varying background colors in a robust and maintenance-free way.
