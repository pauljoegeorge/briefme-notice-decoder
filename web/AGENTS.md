# Web rules

- Keep `src/main.tsx` for mounting providers, `src/app/App.tsx` for route registration, and `src/app/AppShell.tsx` for shared layout. No feature state, fetch calls, or feature markup in `src/app/`.
- Put each page in `src/pages/<PageName>/`, matching its component name. Keep its `components/`, `hooks/`, `api/`, `types/`, `utils/`, and `styles/` inside that folder. Register the URL path explicitly in `App.tsx` so the path-to-page mapping is visible there.
- Use semantic HTML and keyboard-accessible controls. Announce errors with `role="alert"`; show loading and uncertainty clearly.
- Render server text as text. Do not use `dangerouslySetInnerHTML` for notices, OCR, or guide content.
- Use design tokens from `src/styles/tokens.css`; check mobile and dark mode for UI changes.
- Keep network calls in feature API modules. Validate or narrow server responses before relying on them for critical behavior.
- Cancel stale requests and release object URLs or other browser resources when inputs change or a page unmounts. Promote UI to a shared package only after another feature needs it.
