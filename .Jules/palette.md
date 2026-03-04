## 2024-05-18 - Keyboard Accessibility & Reduced Motion
**Learning:** When adding focus outlines on dynamic backgrounds (like gradients), using `currentColor` provides automatic contrast adjustment. Also, `scroll-behavior: smooth` should always be wrapped in a `prefers-reduced-motion` media query to respect accessibility settings.
**Action:** Always test focus states on all background variations and wrap purely aesthetic animations/transitions in reduced motion queries.
