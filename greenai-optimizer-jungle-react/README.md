# AI² Optimizer — Forest / JungleMind Style

A React + Vite + Tailwind CSS hackathon prototype for **AI² Optimizer**, redesigned around the supplied JungleMind forest/glass visual direction.

## Run

Because PowerShell on some Windows machines blocks `npm.ps1`, use the Node executable's command shim directly:

```powershell
& "C:\Program Files\nodejs\npm.cmd" install
& "C:\Program Files\nodejs\npm.cmd" run dev
```

Then open the Vite URL shown in the terminal.

## Included files

- `src/App.jsx` — complete interactive prototype
- `src/index.css` — forest/glass design system, responsive layouts and animations
- `src/main.jsx` — React entry point
- `vite.config.js` — Vite + React + Tailwind configuration
- `package.json` — project dependencies and scripts
- `index.html` — document head, Poppins font and app root

## What is included

- Full-screen sunlit jungle video hero
- JungleMind-inspired minimal navigation and frosted prompt card
- AI² task-complexity classifier
- Small / Medium / Large model routing simulation
- AI Playground
- Sustainability dashboard
- Resource-aware routing visualization
- Performance benchmark view
- Responsive mobile menu
- Forest-green glassmorphism application screens
- Reduced-motion support
- Prototype metrics clearly labeled as estimates/illustrative data

## Backend integration

The current router and responses are simulated in `src/App.jsx`. Replace `classify()` and `runPrompt()` with calls to a FastAPI/Flask orchestration backend when you connect the real models and telemetry.

The project concept calls for energy and carbon values to be measured experimentally or clearly identified as estimates. Keep that distinction in the final demo.
