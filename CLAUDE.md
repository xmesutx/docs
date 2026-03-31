# CLAUDE.md — GitHub Docs Codebase-Leitfaden

Diese Datei bietet Orientierung für KI-Assistenten, die im Repository `github/docs` (docs.github.com) arbeiten.

## Projektübersicht

Dies ist der Quellcode für [docs.github.com](https://docs.github.com) — GitHubs Produktdokumentationsseite. Es handelt sich um eine dynamische Node.js-Webanwendung auf Basis von Express und Next.js, deren Inhalte als Markdown-Dateien mit Liquid-Templating verfasst werden.

**Stack:** Node.js 16, Express, Next.js 11, React 17, TypeScript (Komponenten), JavaScript ESM (lib/middleware/scripts)

---

## Repository-Struktur

```
/
├── content/         # Markdown-Dokumentationsquellen (Englisch)
├── data/            # YAML/Markdown-Daten: Variablen, Reusables, Features, Glossare
├── components/      # React-Komponenten (TSX/TypeScript)
├── lib/             # Kernbibliotheksmodule (JS): Seiten laden, rendern, versionieren
├── middleware/      # Express-Middleware-Kette
├── pages/           # Next.js-Seiten (dateisystembasiertes Routing)
├── script/          # Automatisierungs- und Wartungsskripte
├── tests/           # Jest-Testsuite
├── stylesheets/     # SCSS-Stylesheets
├── translations/    # Übersetzte Inhalte (zh-CN, ja-JP, es-ES, pt-BR, de-DE)
├── includes/        # Liquid-Tag-Implementierungen
├── assets/          # Statische Assets (Bilder)
└── contributing/    # Beitragsleitfäden und Referenzen
```

### Wichtige Dateien

| Datei | Zweck |
|-------|-------|
| `server.mjs` | Einstiegspunkt der Express-App |
| `lib/app.js` | Express-App-Factory (bindet alle Middleware ein) |
| `lib/warm-server.js` | Lädt Seiten-/Weiterleitungsdaten beim Start vor |
| `lib/page.js` | Seitenmodell — lädt, parst und rendert Inhalte |
| `lib/all-versions.js` | Kanonische Liste der Produktversionen |
| `lib/languages.js` | Definitionen der unterstützten Sprachversionen |
| `lib/frontmatter.js` | Frontmatter-Schema und Validierung |
| `next.config.js` | Next.js-Konfiguration |
| `middleware/index.js` | Geordneter Middleware-Stack |
| `content/index.md` | Seitenwurzel — definiert die oberste Produktliste |

---

## Entwicklungsbefehle

```bash
# Abhängigkeiten installieren (saubere Installation; kein npm install verwenden)
npm ci

# Next.js statische Assets bauen (erforderlich vor dem ersten Start und nach git pull)
npm run build

# Dev-Server starten auf http://localhost:4000 (Hot-Reload via nodemon)
npm start          # oder: npm run dev

# Mit allen Sprachen starten
npm run start-all-languages

# Debug-Modus (kompatibel mit VS Code Node-Debugger)
npm run debug

# TypeScript-Typprüfung (kein Ausgabe)
npm run tsc
```

### Testen

```bash
# Gesamte Testsuite ausführen
npm test

# Einzelne Testdatei oder Verzeichnis ausführen
npm test -- tests/unit/page.js
NODE_OPTIONS=--experimental-vm-modules npx jest tests/unit

# Watch-Modus mit Coverage
npm run test-watch

# Browser-/Puppeteer-Tests (setzt vorheriges Build voraus)
npm run browser-test

# Nur Übersetzungsdateien linten
npm run lint-translation

# Barrierefreiheitstests (pa11y)
npm run pa11y-test
```

### Linting & Formatierung

```bash
# ESLint (JS, MJS, TS, TSX)
npm run lint

# Prettier-Prüfung (kein Schreiben)
npm run prettier-check

# Prettier automatisch formatieren
npm run prettier
```

Pre-Commit-Hooks (via husky + lint-staged) führen ESLint und Prettier automatisch auf gestagten Dateien aus.

---

## Konventionen für die Inhaltserstellung

### Speicherort

Die gesamte englische Dokumentation liegt unter `content/`. Die Struktur spiegelt den URL-Pfad wider:
- `content/actions/index.md` → `/en/actions`
- `content/actions/quickstart.md` → `/en/actions/quickstart`

### Frontmatter

Jede Inhaltsdatei **muss** YAML-Frontmatter enthalten. Pflichtfelder:

```yaml
---
title: 'Seitentitel hier'
versions:
  fpt: '*'        # Free, Pro & Team (GitHub.com)
  ghec: '*'       # GitHub Enterprise Cloud
  ghes: '>=3.0'   # GitHub Enterprise Server (SemVer-Bereich)
---
```

Weitere wichtige Frontmatter-Felder:

| Feld | Typ | Zweck |
|------|-----|-------|
| `shortTitle` | string | Verkürzter Titel für Seitenleiste/Breadcrumbs |
| `intro` | string | Einzeilige Seitenbeschreibung |
| `redirect_from` | array | Weiterleitungen von alten URLs |
| `layout` | string | Layout: `default`, `product-landing`, `product-guides`, `release-notes`, `false` |
| `children` | array | Unterseiten-Slugs (für Index-/Kategorieseiten) |
| `type` | string | Anleitungstyp: `overview`, `quick_start`, `tutorial`, `how_to`, `reference` |
| `topics` | array | Kategorisierungstags (müssen in `data/allowed-topics.js` vorhanden sein) |
| `showMiniToc` | boolean | Mini-Inhaltsverzeichnis anzeigen (Standard: true für Artikel) |

### Versionierung

Vier Produktversionen werden in Frontmatter und Liquid verwendet:

| Schlüssel | Produkt |
|-----------|---------|
| `fpt` | Free, Pro & Team (GitHub.com) — wird aus URLs entfernt |
| `ghec` | GitHub Enterprise Cloud |
| `ghes` | GitHub Enterprise Server (nummerierte Releases, z. B. `3.8`) |
| `ghae` | GitHub AE |

**Versionsbereiche** verwenden SemVer-Syntax: `ghes: '>=3.0'`, `ghes: '<3.5'`, `ghes: '*'`

**Inline-Versionierung mit Liquid:**
```liquid
{% ifversion fpt or ghec %}
Dieser Inhalt erscheint nur auf GitHub.com.
{% endif %}

{% ifversion ghes > 3.4 %}
Verfügbar ab GHES 3.5.
{% endif %}
```

### Liquid-Templating

Inhaltsdateien unterstützen [Liquid](https://liquidjs.com/) für dynamische Inhalte:

```liquid
# Wiederverwendbaren Abschnitt einfügen
{% data reusables.actions.actions-use-policy-settings %}

# Variable einfügen
{% data variables.product.prodname_actions %}

# Bedingter Inhalt
{% ifversion fpt %}...{% endif %}

# Hinweis-Callout
{% note %}
**Hinweis:** Dies ist wichtig.
{% endnote %}

# Warnungs-Callout
{% warning %}
**Warnung:** Zerstörerische Aktion voraus.
{% endwarning %}
```

### Reusables und Variablen

- **Reusables** (`data/reusables/`): Mehrere Sätze lange Markdown-Abschnitte, referenziert als `{% data reusables.<pfad> %}`
- **Variablen** (`data/variables/`): Kurze inline Zeichenketten (Produktnamen, URLs), referenziert als `{% data variables.<pfad> %}`
- **Features** (`data/features/`): Feature-Flag-YAML-Dateien für featurebasierte Versionierung

---

## Komponentenentwicklung

Komponenten befinden sich in `components/` und sind in TypeScript/TSX geschrieben. Sie werden server- und clientseitig über Next.js gerendert.

- `.tsx` für React-Komponenten, `.ts` für TypeScript ohne JSX verwenden
- CSS-Module (`.module.scss`) liegen direkt neben den Komponenten
- Primer React (`@primer/react`) ist das Design-System — dessen Komponenten und Tokens verwenden
- Barrierefreiheit wird durch `eslint-plugin-jsx-a11y` erzwungen

TypeScript-Regeln (aus `.eslintrc.js`):
- `@typescript-eslint/no-unused-vars` ist ein Fehler
- `camelcase` ist für TypeScript-Dateien deaktiviert (API-Daten verwenden snake_case)

---

## Testkonventionen

Tests befinden sich in `tests/` und sind nach Typ organisiert:

| Verzeichnis | Was getestet wird |
|-------------|------------------|
| `tests/unit/` | Reine Unit-Tests für Bibliotheksfunktionen |
| `tests/rendering/` | Vollständiges Seiten-Rendering via supertest |
| `tests/routing/` | HTTP-Routing, Weiterleitungen, Header |
| `tests/linting/` | Validierung von Inhalts-/Datendateien |
| `tests/content/` | Inhaltsspezifische Validierungen |
| `tests/graphql/` | GraphQL-Schema-Tests |
| `tests/browser/` | Puppeteer-Browsertests (optionale Abhängigkeiten erforderlich) |

**Wichtige Testkonventionen:**
- Alle Testdateien entsprechen dem Muster `**/tests/**/*.js`
- Dateien in `tests/helpers/` und `tests/fixtures/` werden nicht als Tests ausgeführt
- `jest-expect-message` für aussagekräftige Assertion-Fehlermeldungen verwenden
- CI läuft mit `NODE_OPTIONS='--max_old_space_size=8192 --experimental-vm-modules'`

---

## Middleware-Pipeline

Der Express-Middleware-Stack (`middleware/index.js`) verarbeitet Anfragen in Reihenfolge. Wichtige Middleware:

1. `rate-limit` — API-Ratenbegrenzung
2. `detect-language` — Setzt `req.language` aus URL-Präfix oder `Accept-Language`
3. `context` — Baut `req.context` auf (Seitendaten, Versionen usw.)
4. `find-page` — Sucht das passende `Page`-Objekt
5. `contextualizers/` — Reichert den Kontext an (Lernpfade, empfohlene Links usw.)
6. `render-page` — Rendert die Seite und sendet die Antwort
7. `handle-errors` — Fehlerseiten-Rendering

Das `req.context`-Objekt ist der primäre Datenspeicher für das Seiten-Rendering.

---

## Internationalisierung

- Standardsprache: Englisch (`en`)
- Unterstützt: `en`, `cn` (zh-Hans), `ja`, `es`, `pt`, `de`
- Übersetzungsdateien spiegeln `content/` in `translations/<locale>/` wider
- Crowdin verwaltet die Übersetzungssynchronisierung (konfiguriert in `crowdin.yml`)
- Dev-Server standardmäßig nur `en,ja` — `ENABLED_LANGUAGES`-Umgebungsvariable setzen für weitere
- `data/ui.yml` enthält lokalisierte UI-Zeichenketten

---

## Codestil

Wird automatisch durch ESLint + Prettier erzwungen. Wichtige Regeln:

**JavaScript/TypeScript:**
- Keine Semikolons
- Einfache Anführungszeichen
- `printWidth: 100`
- Pfeilfunktionen: Klammern immer
- `eslint:recommended` + `standard` + `prettier`

**YAML:**
- Einfache Anführungszeichen (Prettier)

Pre-Commit-Hooks nicht überspringen (`--no-verify`). Lint-Probleme vor dem Commit beheben.

---

## Umgebungsvariablen

Siehe `.env.example` für verfügbare Variablen. Die wichtigsten:

| Variable | Zweck |
|----------|-------|
| `PORT` | Server-Port (Standard: 4000) |
| `NODE_ENV` | `development` / `production` / `test` |
| `ENABLED_LANGUAGES` | Kommagetrennte Sprachcodes (z. B. `en,ja`) |

`.env.example` nach `.env` kopieren für lokale Anpassungen.

---

## Skripte

Skripte in `script/` sind JavaScript (kein Bash) für plattformübergreifende Kompatibilität. Wichtige Skripte:

| Skript | Zweck |
|--------|-------|
| `script/rest/update-files.js` | REST-API-Docs aus OpenAPI synchronisieren |
| `script/graphql/` | GraphQL-Schema synchronisieren |
| `script/sync-search-indices.js` | Suchindizes aufbauen und synchronisieren |
| `script/prevent-pushes-to-main.js` | Git-Hook: blockiert direkte Pushes auf main |
| `script/rendered-content-link-checker.mjs` | Interne Links validieren |
| `script/i18n/` | Übersetzungs-Tooling |

---

## Einschränkungen und Hinweise

- **Node.js-Version**: 16.x (erzwungen durch `engines` in package.json und `.node-version`)
- **Nicht direkt auf `main` pushen** — der `prevent-pushes-to-main`-Hook blockiert dies
- **Early-Access-Inhalte** (`content/early-access/`, `data/early-access/`) sind per .gitignore ausgeschlossen und werden separat verwaltet
- **Git LFS** ist für große binäre Assets erforderlich
- **Lizenz**: Inhalte (assets, content, data) sind CC-BY-4.0; sämtlicher sonstiger Code ist MIT
