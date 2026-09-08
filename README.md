# Reel — video merger

Merges video clips entirely in your browser (nothing uploads). Includes
`coi-serviceworker.js` so that once hosted on GitHub Pages, the app can use
FFmpeg's multi-core engine instead of falling back to single-core — GitHub
Pages doesn't let you set the `Cross-Origin-Opener-Policy` /
`Cross-Origin-Embedder-Policy` headers directly, so this service worker
fakes them client-side.

## Put this on GitHub Pages (no git required)

1. Go to https://github.com/new and create a new repository (public, any name — e.g. `reel`).
2. On the empty repo page, click **uploading an existing file**.
3. Drag in all three files from this folder: `index.html`, `coi-serviceworker.js`, `README.md`.
4. Click **Commit changes**.
5. Go to the repo's **Settings → Pages**.
6. Under **Build and deployment → Source**, choose **Deploy from a branch**.
7. Under **Branch**, choose `main` and folder `/ (root)`, then **Save**.
8. Wait ~1 minute, then open the URL GitHub shows you (something like
   `https://yourusername.github.io/reel/`).

The first visit will flicker/reload once — that's the service worker
registering itself. After that, open the browser console and check
`self.crossOriginIsolated` — it should say `true`, and the badge at the top
of the page should read "Multi-core engine active".

## Notes

- Must be served over HTTPS (GitHub Pages does this automatically) — it
  won't work over plain HTTP.
- If you ever get real control over server headers (Netlify, Vercel,
  Cloudflare Pages), you can drop `coi-serviceworker.js` and its `<script>`
  tag and set `Cross-Origin-Opener-Policy: same-origin` and
  `Cross-Origin-Embedder-Policy: require-corp` natively instead — that's
  slightly more robust than the service-worker trick.
