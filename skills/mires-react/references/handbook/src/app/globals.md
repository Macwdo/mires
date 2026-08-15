# Global presentation

The stylesheet uses system fonts, resilient layouts, visible focus, responsive
breakpoints, and a reduced-motion override. Transitions name properties
explicitly.

<!-- artifact: src/app/globals.css; profiles: base,forms,data,auth,realtime,full -->
```css
:root {
  color-scheme: light;
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
  background: #f4f1eb;
  color: #16201d;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
}

button,
input,
select {
  font: inherit;
}

a {
  color: #155f54;
}

:focus-visible {
  outline: 3px solid #d06b32;
  outline-offset: 3px;
}

.skip-link {
  position: fixed;
  inset: 0 auto auto 1rem;
  z-index: 10;
  padding: 0.75rem 1rem;
  background: #16201d;
  color: white;
  transform: translateY(-130%);
  transition: transform 160ms ease;
}

.skip-link:focus {
  transform: translateY(1rem);
}

.shell {
  width: min(100% - 2rem, 68rem);
  margin-inline: auto;
  padding-block: clamp(3rem, 8vw, 8rem);
}

.eyebrow {
  color: #99603e;
  font-size: 0.8rem;
  font-weight: 750;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h1 {
  max-width: 14ch;
  margin-block: 0.5rem 1rem;
  font-size: clamp(2.4rem, 7vw, 5.5rem);
  line-height: 0.95;
  letter-spacing: -0.055em;
}

.lede {
  max-width: 58ch;
  font-size: 1.15rem;
  line-height: 1.7;
}

.tabs {
  margin-block: 2.5rem;
  border: 1px solid #c9c4b9;
  border-radius: 1rem;
  background: #fffdf8;
  box-shadow: 0 1rem 2.5rem rgb(22 32 29 / 8%);
}

.tab-list {
  display: flex;
  gap: 0.25rem;
  overflow-x: auto;
  padding: 0.5rem;
  border-bottom: 1px solid #ded9cf;
}

.tab {
  min-height: 2.75rem;
  padding-inline: 1rem;
  border: 0;
  border-radius: 0.7rem;
  background: transparent;
  color: #40504b;
  cursor: pointer;
}

.tab[aria-selected="true"] {
  background: #dcebe4;
  color: #123d35;
}

.tab-panel {
  padding: clamp(1rem, 4vw, 2rem);
  line-height: 1.6;
}

.stack {
  display: grid;
  gap: 1rem;
}

.field {
  display: grid;
  gap: 0.4rem;
}

.field input,
.field select {
  min-height: 2.75rem;
  width: 100%;
  border: 1px solid #817c72;
  border-radius: 0.6rem;
  padding-inline: 0.75rem;
  background: white;
}

.button {
  min-height: 2.75rem;
  border: 0;
  border-radius: 0.65rem;
  padding-inline: 1rem;
  background: #155f54;
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition:
    background-color 160ms ease,
    transform 160ms ease;
}

.button:hover {
  background: #0f4b42;
}

.button:active {
  transform: translateY(1px);
}

.button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.error {
  color: #a32929;
}

.notice {
  padding: 0.8rem;
  border-radius: 0.6rem;
  background: #edf5f1;
}

.links {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

@media (max-width: 40rem) {
  .shell {
    padding-block: 2.5rem;
  }

  .tab-list {
    scroll-snap-type: x proximity;
  }

  .tab {
    flex: 0 0 auto;
    scroll-snap-align: start;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
```
