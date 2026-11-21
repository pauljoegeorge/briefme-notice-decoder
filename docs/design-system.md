# Design system

The interface helps someone verify a notice. The original image and reading share the screen; source selections connect extracted facts to OCR highlights. Uncertainty and high-risk redirects remain prominent.

## Foundations

- Use semantic CSS custom properties in `web/src/styles/tokens.css`. Add reusable spacing, type, and radius tokens there as the UI grows.
- Use restrained green for actions and evidence, amber for warnings, red for errors. Never encode meaning by color alone.
- Keep a readable system font stack, clear heading hierarchy, and comfortable body line height. Avoid decorative motion around evidence.
- Maintain light/dark themes, a one-column mobile layout, comfortable touch targets, and visible keyboard focus.

## Components and states

- Upload: accepted formats/limits, disabled state, progress state, and actionable error.
- Result: original image, OCR highlights, extracted facts, source selection, confidence, and uncertainty message.
- High risk: limited description plus referral; no implied decision. Money: verify amount and deadline against original.
- Empty/unreadable: explain what failed and how to retry. Never show a confident blank result.

Use semantic HTML first. Check small screens, keyboard navigation, focus, contrast, loading, error, and long Japanese/English text for UI changes.
