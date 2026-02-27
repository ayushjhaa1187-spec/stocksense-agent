## 2024-05-20 - Missing Accessibility Basics (Skip-links & Smooth Scroll)
**Learning:** This app structure lacks basic accessibility features like a "skip to main content" link for keyboard users and accessible smooth scrolling. Memory documented this, but the actual codebase was missing it.
**Action:** Always verify semantic HTML (`<main>`) and keyboard accessibility features (like `.skip-link`) in SPAs to ensure users can bypass repetitive navigation headers. When implementing smooth scrolling, always wrap it in `@media (prefers-reduced-motion: no-preference)` to respect user OS settings.
