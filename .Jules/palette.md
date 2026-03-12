## 2026-02-18 - Improve Interactive Element Visibility
**Learning:** This application lacks visual focus states on its interactive links and buttons. While the hover color indicates interactivity for pointer users, keyboard navigators receive no feedback on what they are currently focusing, which is a major accessibility failing. Adding outline via `:focus-visible` with `currentColor` provides an adaptive focus outline.
**Action:** Always implement a `:focus-visible` outline pattern using `currentColor` on custom frontends to ensure interactive elements consistently display a high-contrast focus indicator regardless of the specific component's background color.

## 2026-02-18 - Redundant Decorative Emojis
**Learning:** The landing page uses emojis wrapped in `.feature-icon` elements purely for decorative purposes alongside descriptive `<h3>` tags. Screen readers will read both the emoji name and the heading, creating a redundant and confusing experience for users.
**Action:** Decorative elements that accompany adjacent text providing the same semantic meaning should always have `aria-hidden="true"` applied to remove them from the accessibility tree and prevent redundant announcements.
