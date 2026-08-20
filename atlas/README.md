# Field atlas (standalone page)

Positioning page for the academy: who it is for, what is inside, what not to expect, and a filterable field map.

This folder is a static SPA. It does not import the React applet.

## Open it

With the academy server:

```bash
npm run dev
```

Then visit `http://localhost:3000/atlas/`.

Standalone (no Node):

```bash
# from this folder
python3 -m http.server 4173
```

Then visit `http://localhost:4173/`. Opening `index.html` as a `file://` URL also works; the “Open the applet” button hides in that case.
