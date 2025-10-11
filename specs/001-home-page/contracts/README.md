# Contracts: Home Page

**Feature**: Home Page  
**Branch**: 001-home-page  
**Date**: 2025-10-12  
**Phase**: 1 - Design & Contracts

## Overview

This feature is a **static site** built with Hugo, not a web application with API endpoints. Therefore, traditional API contracts (REST/GraphQL schemas) are not applicable.

Instead, this directory documents the "contracts" between different parts of the Hugo system:

1. **Hugo Template Contracts** - Expected data structures for layouts
2. **Content Contracts** - Required frontmatter fields for content types
3. **JavaScript Contracts** - DOM interfaces for theme switcher

---

## 1. Hugo Template Contracts

### Home Page Layout (`layouts/index.html`)

**Expected Context** (`.` in template):

```go
type HomePage struct {
    Title       string              // Site title from hugo.toml
    Description string              // Site description from params
    Params      PageParams          // Page-specific parameters
    Site        SiteInfo            // Global site information
    Pages       []Page              // All pages (for article list)
}

type PageParams struct {
    Tagline string                  // Hero tagline
    Image   string                  // OG image path (optional)
}

type SiteInfo struct {
    Title           string          // "Гише безкрайност"
    BaseURL         string          // "https://gishe8.com/"
    LanguageCode    string          // "bg-BG"
    RegularPages    []Page          // All regular pages (articles)
    Params          SiteParams      // Global parameters
}

type SiteParams struct {
    Description        string       // Site description
    DefaultTheme       string       // "light", "dark", "system"
    HomeArticleCount   int          // Number of articles on home (5)
    ExcerptLength      int          // Summary length (150)
}
```

**Template Usage Example**:

```go-html-template
{{ define "main" }}
  <!-- Hero Section -->
  <section class="hero">
    <h1>{{ .Site.Title }}</h1>
    <p>{{ .Params.tagline }}</p>
  </section>

  <!-- Article List -->
  <section class="articles">
    {{- $articles := where .Site.RegularPages "Type" "article" -}}
    {{- $articles = where $articles "Draft" false -}}
    {{- $articles = $articles | first (.Site.Params.homeArticleCount | default 5) -}}
    
    {{- range $articles -}}
      {{ partial "article-card.html" . }}
    {{- end -}}
  </section>
{{ end }}
```

---

### Article Card Partial (`layouts/_partials/article-card.html`)

**Expected Context** (`.` in partial):

```go
type Article struct {
    Title           string          // Article title
    Date            time.Time       // Publication date
    Description     string          // Summary/excerpt
    Permalink       string          // Article URL
    Params          ArticleParams   // Article frontmatter
    Summary         string          // Auto-generated summary (fallback)
}

type ArticleParams struct {
    FeaturedImage   string          // Optional featured image
    ImageAlt        string          // Alt text for image (required if image exists)
    Tags            []string        // Article tags
    Categories      []string        // Article categories
}
```

**Partial Usage Example**:

```go-html-template
<!-- article-card.html -->
<article class="article-card">
  {{ with .Params.featured_image }}
    <img src="{{ . }}" alt="{{ $.Params.image_alt }}" loading="lazy">
  {{ end }}
  
  <h2>
    <a href="{{ .Permalink }}">{{ .Title }}</a>
  </h2>
  
  <time datetime="{{ .Date.Format "2006-01-02" }}">
    {{ .Date.Format "2 January 2006" }}
  </time>
  
  <p>{{ .Description | default .Summary | truncate 150 }}</p>
  
  {{ with .Params.tags }}
    <div class="tags">
      {{ range . }}
        <span class="tag">{{ . }}</span>
      {{ end }}
    </div>
  {{ end }}
</article>
```

---

## 2. Content Contracts

### Home Page Content (`content/_index.md`)

**Required Frontmatter**:

```yaml
title: string       # REQUIRED - Site/page title
description: string # REQUIRED - Meta description
tagline: string     # REQUIRED - Hero section tagline
```

**Optional Frontmatter**:

```yaml
image: string       # Social sharing image path
keywords: []string  # SEO keywords
type: string        # Content type override (default: "home")
```

**Contract Enforcement**: Hugo will build without these fields, but SEO and UX will be degraded. Consider validation in CI/CD.

---

### Article Content (`content/article/*.md`)

**Required Frontmatter**:

```yaml
title: string           # REQUIRED - Article title (max 80 chars recommended)
date: RFC3339           # REQUIRED - ISO 8601 datetime
draft: boolean          # REQUIRED - Publication status
description: string     # REQUIRED - Summary (100-150 chars recommended)
```

**Optional Frontmatter**:

```yaml
author: string          # Author name
tags: []string          # Article tags (max 5 recommended)
categories: []string    # Article categories (max 3 recommended)
featured_image: string  # Featured image path (relative to article bundle)
image_alt: string       # Alt text (REQUIRED if featured_image exists)
weight: integer         # Manual sort order (lower = higher priority)
```

**Validation Rules**:

- If `featured_image` is set, `image_alt` MUST be provided (accessibility requirement)
- `title` should be ≤80 characters (will be truncated in UI with ellipsis)
- `description` should be 100-150 characters (optimal for previews and SEO)
- `date` must be valid RFC3339/ISO 8601 format

---

## 3. JavaScript Contracts

### Theme Switcher Interface

**DOM Structure Contract**:

The HTML must provide theme toggle buttons with specific data attributes:

```html
<!-- Theme switcher buttons -->
<button type="button" 
        data-theme-toggle="light" 
        aria-label="Превключи на светла тема">
  <!-- Icon -->
</button>

<button type="button" 
        data-theme-toggle="dark" 
        aria-label="Превключи на тъмна тема">
  <!-- Icon -->
</button>

<button type="button" 
        data-theme-toggle="system" 
        aria-label="Използвай системната тема">
  <!-- Icon -->
</button>
```

**Required Attributes**:

- `data-theme-toggle`: Must be one of `"light"`, `"dark"`, `"system"`
- `aria-label`: Descriptive label in Bulgarian for screen readers

**JavaScript Behavior Contract**:

```javascript
// On button click
// 1. Get theme value from data-theme-toggle attribute
// 2. Apply theme to :root element via data-theme attribute
document.documentElement.setAttribute('data-theme', theme);

// 3. Save preference to localStorage
localStorage.setItem('gishe-theme', theme);

// 4. Update button states (aria-pressed, visual indicators)
```

**CSS Contract**:

CSS must respond to `data-theme` attribute on `:root`:

```css
/* Light theme */
:root[data-theme="light"] {
  --bg-primary: #ffffff;
  --text-primary: #000000;
  /* ... */
}

/* Dark theme */
:root[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --text-primary: #ffffff;
  /* ... */
}

/* System theme (follows prefers-color-scheme) */
:root[data-theme="system"] {
  /* Inherit from media query */
}

@media (prefers-color-scheme: dark) {
  :root[data-theme="system"] {
    /* Dark theme variables */
  }
}
```

---

### LocalStorage Contract

**Key**: `gishe-theme`

**Value Type**: `string`

**Possible Values**: `"light"`, `"dark"`, `"system"`

**Default**: `"system"` (if key doesn't exist)

**Read/Write Example**:

```javascript
// Read
const theme = localStorage.getItem('gishe-theme') || 'system';

// Write
localStorage.setItem('gishe-theme', 'dark');

// Clear (reset to default)
localStorage.removeItem('gishe-theme');
```

---

## 4. Hugo Configuration Contract

### Required Hugo Config (`hugo.toml`)

**Basic Configuration**:

```toml
baseURL = 'https://gishe8.com/'
languageCode = 'bg-BG'
title = 'Гише безкрайност'
theme = 'sarcastic'
defaultContentLanguage = 'bg'
```

**Required Parameters**:

```toml
[params]
  description = string      # REQUIRED - Site description
  homeArticleCount = int    # REQUIRED - Articles on home page (default: 5)
  excerptLength = int       # REQUIRED - Summary length (default: 150)
  defaultTheme = string     # REQUIRED - "light", "dark", or "system" (default: "system")
```

**Optional Parameters**:

```toml
[params]
  author = string           # Site author
  keywords = []string       # Global SEO keywords
  twitter = string          # Twitter handle
  facebook = string         # Facebook page
  imageProcessing = bool    # Enable Hugo image processing (default: true)
  lazyLoadImages = bool     # Enable lazy loading (default: true)
```

---

## 5. Asset Processing Contracts

### CSS Processing Pipeline

**Input**: `themes/sarcastic/assets/css/main.css`

**Process**: 
1. TailwindCSS processing (via PostCSS)
2. Autoprefixer (vendor prefixes)
3. Minification (production only)
4. Fingerprinting (production only)

**Output**: `/css/main.[fingerprint].css`

**Template Reference**:

```go-html-template
{{- $css := resources.Get "css/main.css" -}}
{{- $css = $css | resources.PostCSS -}}
{{- if hugo.IsProduction -}}
  {{- $css = $css | minify | fingerprint -}}
{{- end -}}
<link rel="stylesheet" href="{{ $css.RelPermalink }}">
```

---

### JavaScript Processing Pipeline

**Input**: `themes/sarcastic/assets/js/theme-switcher.js`

**Process**:
1. js.Build (optional, for ES6 imports)
2. Minification (production only)
3. Fingerprinting (production only)

**Output**: `/js/theme-switcher.[fingerprint].js`

**Template Reference**:

```go-html-template
{{- $js := resources.Get "js/theme-switcher.js" -}}
{{- if hugo.IsProduction -}}
  {{- $js = $js | minify | fingerprint -}}
{{- end -}}
<script src="{{ $js.RelPermalink }}" defer></script>
```

---

## 6. SEO Metadata Contracts

### Open Graph Tags (Required)

```html
<meta property="og:title" content="[Page Title] | [Site Title]">
<meta property="og:description" content="[Page Description]">
<meta property="og:type" content="website">  <!-- or "article" for articles -->
<meta property="og:url" content="[Canonical URL]">
<meta property="og:locale" content="bg_BG">
<meta property="og:site_name" content="[Site Title]">
<meta property="og:image" content="[Absolute Image URL]">  <!-- Optional but recommended -->
```

---

### Twitter Card Tags (Required)

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="[Page Title]">
<meta name="twitter:description" content="[Page Description]">
<meta name="twitter:image" content="[Absolute Image URL]">  <!-- Optional but recommended -->
```

---

### JSON-LD Structured Data (Required for Home Page)

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "[Site Title]",
  "url": "[Site Base URL]",
  "description": "[Site Description]",
  "inLanguage": "bg-BG",
  "publisher": {
    "@type": "Organization",
    "name": "[Site Title]",
    "logo": {
      "@type": "ImageObject",
      "url": "[Logo URL]"
    }
  }
}
```

---

## 7. Accessibility Contracts

### Required ARIA Labels (Bulgarian)

| Element | ARIA Attribute | Bulgarian Text Example |
|---------|---------------|------------------------|
| Main navigation | `aria-label` | "Главно меню" |
| Theme switcher | `aria-label` | "Превключи на светла тема" |
| Skip link | `aria-label` | "Към основното съдържание" |
| Article list | `aria-labelledby` | Reference to heading id |
| Decorative images | `aria-hidden` | "true" |

### Focus Order Contract

Keyboard navigation (Tab key) must follow logical reading order:

1. Skip link (initially hidden, visible on focus)
2. Main navigation links
3. Theme switcher buttons
4. Article cards (in chronological order)
5. Footer links

All interactive elements must have visible focus indicators.

---

## Summary

**Total Contracts Documented**: 7

1. ✅ Hugo Template Contracts (expected data structures)
2. ✅ Content Contracts (required frontmatter fields)
3. ✅ JavaScript Contracts (DOM interfaces, localStorage)
4. ✅ Hugo Configuration Contract (required params)
5. ✅ Asset Processing Contracts (CSS/JS pipelines)
6. ✅ SEO Metadata Contracts (OG, Twitter, JSON-LD)
7. ✅ Accessibility Contracts (ARIA, focus order)

**Key Differences from API Contracts**:

- No HTTP endpoints (static site)
- No request/response schemas
- Contracts are between Hugo templates, content files, and JavaScript
- Validation is at build time (Hugo) and runtime (browser)

These contracts ensure consistency between:
- Content creators (writing markdown)
- Theme developers (writing templates)
- JavaScript developers (writing theme switcher)
- SEO/accessibility requirements
