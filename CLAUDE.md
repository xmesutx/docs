# CLAUDE.md — GitHub Docs Codebase Guide

This file provides guidance for AI assistants working in the `github/docs` repository (docs.github.com).

## Project Overview

This is the source for [docs.github.com](https://docs.github.com) — GitHub's product documentation site. It is a dynamic Node.js web application powered by Express and Next.js, with Markdown content files authored using Liquid templating.

**Stack:** Node.js 16, Express, Next.js 11, React 17, TypeScript (components), JavaScript ESM (lib/middleware/scripts)

---

## Repository Structure

```
/
├── content/         # Markdown documentation source (English)
├── data/            # YAML/Markdown data: variables, reusables, features, glossaries
├── components/      # React components (TSX/TypeScript)
├── lib/             # Core library modules (JS): page loading, rendering, versioning
├── middleware/      # Express middleware chain
├── pages/           # Next.js pages (file-system routing)
├── script/          # Automation/maintenance scripts
├── tests/           # Jest test suite
├── stylesheets/     # SCSS stylesheets
├── translations/    # Translated content (zh-CN, ja-JP, es-ES, pt-BR, de-DE)
├── includes/        # Liquid tag implementations
├── assets/          # Static assets (images)
└── contributing/    # Contributor guides and references
```

### Key Files

| File | Purpose |
|------|---------|
| `server.mjs` | Express app entry point |
| `lib/app.js` | Express app factory (mounts all middleware) |
| `lib/warm-server.js` | Preloads page/redirect data at startup |
| `lib/page.js` | Page model — loads, parses, renders content |
| `lib/all-versions.js` | Canonical list of product versions |
| `lib/languages.js` | Supported locale definitions |
| `lib/frontmatter.js` | Frontmatter schema and validation |
| `next.config.js` | Next.js configuration |
| `middleware/index.js` | Ordered middleware stack |
| `content/index.md` | Site root — defines top-level product list |

---

## Development Commands

```bash
# Install dependencies (clean install; do not use npm install)
npm ci

# Build Next.js static assets (required before first run and after pulling)
npm run build

# Start dev server at http://localhost:4000 (hot reload via nodemon)
npm start          # or: npm run dev

# Start with all languages enabled
npm run start-all-languages

# Debug mode (VS Code Node debugger compatible)
npm run debug

# TypeScript type check (no emit)
npm run tsc
```

### Testing

```bash
# Run full test suite
npm test

# Run a specific test file or directory
npm test -- tests/unit/page.js
NODE_OPTIONS=--experimental-vm-modules npx jest tests/unit

# Watch mode with coverage
npm run test-watch

# Browser/puppeteer tests (requires build first)
npm run browser-test

# Lint translation files only
npm run lint-translation

# Accessibility tests (pa11y)
npm run pa11y-test
```

### Linting & Formatting

```bash
# ESLint (JS, MJS, TS, TSX)
npm run lint

# Prettier check (no write)
npm run prettier-check

# Prettier auto-format
npm run prettier
```

Pre-commit hooks (via husky + lint-staged) automatically run ESLint and Prettier on staged files.

---

## Content Authoring Conventions

### File Location

All English documentation lives under `content/`. Structure mirrors the URL path:
- `content/actions/index.md` → `/en/actions`
- `content/actions/quickstart.md` → `/en/actions/quickstart`

### Frontmatter

Every content file **must** include YAML frontmatter. Required fields:

```yaml
---
title: 'Page title here'
versions:
  fpt: '*'        # Free, Pro & Team (GitHub.com)
  ghec: '*'       # GitHub Enterprise Cloud
  ghes: '>=3.0'   # GitHub Enterprise Server (SemVer range)
---
```

Other important frontmatter fields:

| Field | Type | Purpose |
|-------|------|---------|
| `shortTitle` | string | Shortened title for sidebar/breadcrumbs |
| `intro` | string | One-sentence page description |
| `redirect_from` | array | Legacy URL redirects |
| `layout` | string | Layout: `default`, `product-landing`, `product-guides`, `release-notes`, `false` |
| `children` | array | Sub-page slugs (for index/category pages) |
| `type` | string | Guide type: `overview`, `quick_start`, `tutorial`, `how_to`, `reference` |
| `topics` | array | Categorization tags (must be in `data/allowed-topics.js`) |
| `showMiniToc` | boolean | Show mini table of contents (default: true for articles) |

### Versioning

Four product versions are used in frontmatter and Liquid:

| Key | Product |
|-----|---------|
| `fpt` | Free, Pro & Team (GitHub.com) — stripped from URLs |
| `ghec` | GitHub Enterprise Cloud |
| `ghes` | GitHub Enterprise Server (numbered releases, e.g. `3.8`) |
| `ghae` | GitHub AE |

**Version ranges** use SemVer syntax: `ghes: '>=3.0'`, `ghes: '<3.5'`, `ghes: '*'`

**Inline versioning with Liquid:**
```liquid
{% ifversion fpt or ghec %}
This content only appears on GitHub.com.
{% endif %}

{% ifversion ghes > 3.4 %}
Available since GHES 3.5.
{% endif %}
```

### Liquid Templating

Content files support [Liquid](https://liquidjs.com/) for dynamic content:

```liquid
# Insert a reusable snippet
{% data reusables.actions.actions-use-policy-settings %}

# Insert a variable
{% data variables.product.prodname_actions %}

# Conditional content
{% ifversion fpt %}...{% endif %}

# Note callout
{% note %}
**Note:** This is important.
{% endnote %}

# Warning callout
{% warning %}
**Warning:** Destructive action ahead.
{% endwarning %}
```

### Reusables and Variables

- **Reusables** (`data/reusables/`): Multi-sentence Markdown snippets, referenced as `{% data reusables.<path> %}`
- **Variables** (`data/variables/`): Short inline strings (product names, URLs), referenced as `{% data variables.<path> %}`
- **Features** (`data/features/`): Feature-flag YAML files for feature-based versioning

---

## Component Development

Components live in `components/` and are written in TypeScript/TSX. They are rendered server-side and client-side via Next.js.

- Use `.tsx` for React components, `.ts` for non-JSX TypeScript
- CSS Modules (`.module.scss`) are co-located with components
- Primer React (`@primer/react`) is the design system — use its components and tokens
- Accessibility is enforced by `eslint-plugin-jsx-a11y`

TypeScript rules (from `.eslintrc.js`):
- `@typescript-eslint/no-unused-vars` is an error
- `camelcase` is off for TypeScript files (API data uses snake_case)

---

## Testing Conventions

Tests live in `tests/` and are organized by type:

| Directory | What it tests |
|-----------|--------------|
| `tests/unit/` | Pure library function unit tests |
| `tests/rendering/` | Full page rendering via supertest |
| `tests/routing/` | HTTP routing, redirects, headers |
| `tests/linting/` | Content/data file validation |
| `tests/content/` | Content-specific validations |
| `tests/graphql/` | GraphQL schema tests |
| `tests/browser/` | Puppeteer browser tests (optional deps required) |

**Key test conventions:**
- All test files match `**/tests/**/*.js`
- Test files in `tests/helpers/` and `tests/fixtures/` are not run as tests
- Use `jest-expect-message` for descriptive assertion failures
- CI runs with `NODE_OPTIONS='--max_old_space_size=8192 --experimental-vm-modules'`

---

## Middleware Pipeline

The Express middleware stack (`middleware/index.js`) processes requests in order. Key middleware:

1. `rate-limit` — API rate limiting
2. `detect-language` — Sets `req.language` from URL prefix or `Accept-Language`
3. `context` — Builds `req.context` (page data, versions, etc.)
4. `find-page` — Looks up the matching `Page` object
5. `contextualizers/` — Enriches context (learning tracks, featured links, etc.)
6. `render-page` — Renders the page and sends the response
7. `handle-errors` — Error page rendering

The `req.context` object is the primary data carrier for page rendering.

---

## Internationalization

- Default language: English (`en`)
- Supported: `en`, `cn` (zh-Hans), `ja`, `es`, `pt`, `de`
- Translation files mirror `content/` in `translations/<locale>/`
- Crowdin manages translation syncing (configured in `crowdin.yml`)
- Dev server defaults to `en,ja` only — set `ENABLED_LANGUAGES` env var to enable others
- `data/ui.yml` contains localized UI strings

---

## Code Style

Enforced automatically by ESLint + Prettier. Key rules:

**JavaScript/TypeScript:**
- No semicolons
- Single quotes
- `printWidth: 100`
- Arrow function parens: always
- `eslint:recommended` + `standard` + `prettier`

**YAML:**
- Single quotes (Prettier)

Do not skip pre-commit hooks (`--no-verify`). Fix lint issues before committing.

---

## Environment Variables

See `.env.example` for available variables. Key ones:

| Variable | Purpose |
|----------|---------|
| `PORT` | Server port (default: 4000) |
| `NODE_ENV` | `development` / `production` / `test` |
| `ENABLED_LANGUAGES` | Comma-separated language codes (e.g. `en,ja`) |

Copy `.env.example` to `.env` for local overrides.

---

## Scripts

Scripts in `script/` are JavaScript (not Bash) for cross-platform compatibility. Key scripts:

| Script | Purpose |
|--------|---------|
| `script/rest/update-files.js` | Sync REST API docs from OpenAPI |
| `script/graphql/` | Sync GraphQL schema |
| `script/sync-search-indices.js` | Build and sync search indexes |
| `script/prevent-pushes-to-main.js` | Git hook: blocks direct pushes to main |
| `script/rendered-content-link-checker.mjs` | Validate internal links |
| `script/i18n/` | Translation tooling |

---

## Restrictions and Notes

- **Node.js version**: 16.x (enforced by `engines` in package.json and `.node-version`)
- **Do not push to `main`** directly — the `prevent-pushes-to-main` hook blocks this
- **Early-access content** (`content/early-access/`, `data/early-access/`) is gitignored and managed separately
- **Git LFS** is required for large binary assets
- **License**: Content (assets, content, data) is CC-BY-4.0; all other code is MIT
