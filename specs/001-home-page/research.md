# Research: Home Page Implementation

**Feature**: Home Page  
**Branch**: 001-home-page  
**Date**: 2025-10-12  
**Phase**: 0 - Research & Technical Investigation

## Overview

This document consolidates research findings for implementing the GisheNomerBezkrajnost home page. All technical decisions align with the project constitution's principles: Performance & Mobile-First, Bulgarian Content & Satirical Voice, Hugo Best Practices, Minimal External Dependencies, Accessibility & SEO Excellence, Modern Design System, and Monetization Readiness.

## Research Areas

### 1. Hugo Extended & TailwindCSS Integration

**Decision**: Use Hugo Pipes with PostCSS for TailwindCSS processing

**Rationale**:
- Hugo Extended (v0.135+) has built-in support for PostCSS processing via Hugo Pipes
- No need for separate Node.js build process - Hugo handles CSS compilation
- Automatic minification, fingerprinting, and cache busting via Hugo Pipes
- Aligns with Constitution Principle III (Hugo Best Practices) and IV (Minimal Dependencies)

**Implementation Approach**:
```bash
# Install Hugo Extended (required for Tailwind)
brew install hugo  # macOS (includes Extended by default)
# or download from https://github.com/gohugoio/hugo/releases

# Install Tailwind and dependencies (minimal set)
npm init -y
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
```

**Configuration Files Needed**:
- `tailwind.config.js` - Tailwind configuration with Cyrillic font stack
- `postcss.config.js` - PostCSS configuration for Hugo Pipes
- `themes/sarcastic/assets/css/main.css` - Tailwind directives + custom utilities

**Hugo Pipes Usage**:
```go-html-template
{{- $css := resources.Get "css/main.css" -}}
{{- $css = $css | resources.PostCSS -}}
{{- if hugo.IsProduction -}}
  {{- $css = $css | minify | fingerprint -}}
{{- end -}}
<link rel="stylesheet" href="{{ $css.RelPermalink }}">
```

**Alternatives Considered**:
- Pure CSS without framework → Rejected: Too much custom code, harder to maintain
- Bootstrap → Rejected: Heavier bundle, not optimized for modern design
- External CDN for Tailwind → Rejected: Violates Principle IV (self-hosted critical assets)

**References**:
- Hugo Pipes documentation: <https://gohugo.io/hugo-pipes/postcss/>
- Tailwind with Hugo guide: <https://tailwindcss.com/docs/installation/using-postcss>

---

### 2. Modern Cyrillic Font Selection

**Decision**: Use Inter font family with full Cyrillic support, self-hosted via Google Fonts API or local files

**Rationale**:
- Inter has excellent Cyrillic coverage (includes Bulgarian characters)
- Modern, clean, highly readable on screens (OpenType features, variable font support)
- Open-source (OFL license), free to self-host
- Wide range of weights (100-900) for design flexibility
- Optimized for screen rendering with good hinting

**Implementation Approach**:

Option A - Google Fonts with font-display: swap:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap&subset=cyrillic" rel="stylesheet">
```

Option B - Self-hosted (preferred for production):
```bash
# Download Inter from Google Fonts or official GitHub
# Place in themes/sarcastic/static/fonts/
# Use @font-face in CSS
```

**CSS Configuration**:
```css
/* tailwind.config.js */
fontFamily: {
  sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
  display: ['Inter', 'system-ui', 'sans-serif']
}
```

**Alternatives Considered**:
- SF Pro Display → Rejected: Licensing issues for web use, not open-source
- Roboto → Considered: Good fallback but Inter has better screen rendering
- System fonts only → Rejected: Inconsistent appearance across platforms
- Noto Sans → Considered: Good Cyrillic support but heavier file size

**References**:
- Inter official site: <https://rsms.me/inter/>
- Google Fonts Inter: <https://fonts.google.com/specimen/Inter>
- Font subsetting tool: <https://everythingfonts.com/subsetter>

---

### 3. Theme Switcher Implementation (Light/Dark/System)

**Decision**: Use vanilla JavaScript with CSS variables and localStorage persistence

**Rationale**:
- No framework needed for this simple functionality (aligns with Principle IV)
- CSS custom properties enable instant theme switching without page reload
- localStorage provides persistence across sessions
- prefers-color-scheme media query for system theme detection
- ~50 lines of vanilla JS, <2KB minified

**Implementation Approach**:

**CSS Structure**:
```css
/* themes/light.css */
:root[data-theme="light"] {
  --bg-primary: #ffffff;
  --text-primary: #000000;
  --accent: #0066cc;
  /* ... more variables */
}

/* themes/dark.css */
:root[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --text-primary: #ffffff;
  --accent: #66b3ff;
  /* ... more variables */
}

/* Default to system preference */
@media (prefers-color-scheme: dark) {
  :root[data-theme="system"] {
    /* dark theme variables */
  }
}
```

**JavaScript Logic**:
```javascript
// themes/sarcastic/assets/js/theme-switcher.js
(function() {
  'use strict';
  
  const THEME_KEY = 'gishe-theme';
  const THEMES = ['light', 'dark', 'system'];
  
  function getPreferredTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored && THEMES.includes(stored)) return stored;
    return 'system'; // default
  }
  
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }
  
  function initThemeSwitcher() {
    const theme = getPreferredTheme();
    applyTheme(theme);
    
    // Add event listeners to theme buttons
    document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const newTheme = e.target.dataset.themeToggle;
        applyTheme(newTheme);
      });
    });
  }
  
  // Apply immediately to prevent flash
  applyTheme(getPreferredTheme());
  
  // Initialize after DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeSwitcher);
  } else {
    initThemeSwitcher();
  }
})();
```

**Preventing Flash of Unstyled Content (FOUC)**:
- Inline critical theme script in `<head>` before CSS
- Apply theme immediately before page renders
- Use `data-theme` attribute on `:root` element

**Alternatives Considered**:
- CSS-only with checkbox hack → Rejected: Can't persist preference
- React/Vue theme library → Rejected: Violates Principle IV (minimal dependencies)
- Separate CSS files per theme → Rejected: Causes flash during switch

**References**:
- CSS custom properties: <https://developer.mozilla.org/en-US/docs/Web/CSS/--*>
- prefers-color-scheme: <https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme>
- Web.dev theme switching: <https://web.dev/prefers-color-scheme/>

---

### 4. Performance Optimization Strategies

**Decision**: Multi-layered approach using Hugo's built-in features, lazy loading, and critical CSS inlining

**Rationale**:
- Target <2s load on 3G requires aggressive optimization
- Hugo's built-in minification and fingerprinting are zero-config
- Critical CSS inlining eliminates render-blocking resources
- Lazy loading defers non-critical images

**Optimization Techniques**:

**1. Hugo Asset Pipeline**:
```go-html-template
{{- $css := resources.Get "css/main.css" | resources.PostCSS | minify | fingerprint -}}
{{- $js := resources.Get "js/theme-switcher.js" | js.Build | minify | fingerprint -}}
```

**2. Critical CSS Extraction**:
- Inline above-the-fold styles in `<head>`
- Load full stylesheet with `media="print" onload="this.media='all'"`
- Use Hugo's `.Content` for inline styles

**3. Image Optimization**:
```go-html-template
{{- with .Resources.GetMatch "featured-image.*" -}}
  {{- $image := .Resize "800x webp q85" -}}
  <img src="{{ $image.RelPermalink }}" 
       loading="lazy" 
       alt="{{ $.Params.imageAlt }}"
       width="{{ $image.Width }}" 
       height="{{ $image.Height }}">
{{- end -}}
```

**4. Font Loading Strategy**:
```html
<link rel="preload" href="/fonts/Inter-Regular.woff2" as="font" type="font/woff2" crossorigin>
<style>
  @font-face {
    font-family: 'Inter';
    font-display: swap; /* Prevents FOIT */
    src: url('/fonts/Inter-Regular.woff2') format('woff2');
  }
</style>
```

**5. JavaScript Strategy**:
- Inline theme switcher (<2KB) to prevent FOUC
- No external JS libraries
- Use `defer` or `async` for non-critical scripts

**6. Resource Hints**:
```html
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

**Core Web Vitals Targets**:
- **LCP (Largest Contentful Paint)** <2.5s: Optimize hero section rendering, inline critical CSS
- **FID (First Input Delay)** <100ms: Minimal JavaScript, no blocking scripts
- **CLS (Cumulative Layout Shift)** <0.1: Reserve space for images with width/height, no layout shifts during theme switch

**Alternatives Considered**:
- Service Worker caching → Deferred: Adds complexity, implement in future iteration
- HTTP/2 Server Push → Rejected: Not supported by all CDNs, diminishing returns
- AMP (Accelerated Mobile Pages) → Rejected: Too restrictive, limits design flexibility

**References**:
- Web Vitals: <https://web.dev/vitals/>
- Hugo image processing: <https://gohugo.io/content-management/image-processing/>
- Critical CSS techniques: <https://web.dev/extract-critical-css/>

---

### 5. Accessibility (WCAG 2.1 Level AA) Implementation

**Decision**: Semantic HTML5 + ARIA labels + keyboard navigation + color contrast validation

**Rationale**:
- WCAG 2.1 Level AA is constitutional requirement (Principle V)
- Semantic HTML provides ~80% of accessibility for free
- ARIA enhances where semantic HTML is insufficient
- Keyboard navigation is critical for non-mouse users

**Implementation Checklist**:

**1. Semantic HTML Structure**:
```html
<header role="banner">
  <nav role="navigation" aria-label="Главно меню">...</nav>
</header>
<main role="main" id="main-content">
  <section aria-labelledby="hero-heading">...</section>
  <section aria-labelledby="articles-heading">...</section>
</main>
<footer role="contentinfo">...</footer>
```

**2. ARIA Labels for Theme Switcher**:
```html
<button type="button" 
        aria-label="Превключи на светла тема" 
        aria-pressed="false"
        data-theme-toggle="light">
  <svg aria-hidden="true"><!-- sun icon --></svg>
  <span class="sr-only">Светла</span>
</button>
```

**3. Color Contrast Requirements**:
- Normal text (16px): 4.5:1 minimum
- Large text (18px bold or 24px): 3:1 minimum
- Use contrast checker during design: <https://webaim.org/resources/contrastchecker/>

**4. Keyboard Navigation**:
- All interactive elements tabbable (native focus order)
- Visible focus indicators (outline or custom style)
- Skip link to main content: `<a href="#main-content" class="sr-only">Към основното съдържание</a>`

**5. Image Alt Text**:
- Meaningful descriptions in Bulgarian
- Empty alt for decorative images: `alt=""`
- Satirical but descriptive: `alt="Чиновник спи на гише номер 8 от 2007 година"`

**6. Screen Reader Testing**:
- Test with NVDA (Windows) or VoiceOver (macOS/iOS)
- Verify reading order matches visual order
- Check form labels and button descriptions

**7. Screen Reader Only Text**:
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

**Alternatives Considered**:
- Skip ARIA, use semantic HTML only → Rejected: Insufficient for complex UI (theme switcher)
- Accessibility overlay widget → Rejected: Band-aid solution, doesn't fix core issues

**References**:
- WCAG 2.1 Quick Reference: <https://www.w3.org/WAI/WCAG21/quickref/>
- WebAIM ARIA guide: <https://webaim.org/techniques/aria/>
- A11y checklist: <https://www.a11yproject.com/checklist/>

---

### 6. SEO & Structured Data Best Practices

**Decision**: Implement Open Graph, Twitter Cards, and JSON-LD structured data using Hugo templates

**Rationale**:
- SEO is critical for organic growth (Principle V)
- Structured data improves search result appearance
- Social sharing metadata drives traffic from social media
- Hugo's templating makes this easy to maintain

**Implementation Components**:

**1. Meta Tags Template** (`themes/sarcastic/layouts/_partials/head.html`):
```html
<!-- Basic Meta -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{{ .Description | default .Site.Params.description }}">
<meta name="language" content="bg-BG">
<link rel="canonical" href="{{ .Permalink }}">

<!-- Open Graph -->
<meta property="og:title" content="{{ .Title }} | {{ .Site.Title }}">
<meta property="og:description" content="{{ .Description | default .Site.Params.description }}">
<meta property="og:type" content="{{ if .IsPage }}article{{ else }}website{{ end }}">
<meta property="og:url" content="{{ .Permalink }}">
<meta property="og:locale" content="bg_BG">
<meta property="og:site_name" content="{{ .Site.Title }}">
{{ with .Params.image }}<meta property="og:image" content="{{ . | absURL }}">{{ end }}

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ .Title }}">
<meta name="twitter:description" content="{{ .Description | default .Site.Params.description }}">
{{ with .Params.image }}<meta name="twitter:image" content="{{ . | absURL }}">{{ end }}
```

**2. JSON-LD Structured Data** (for home page):
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "{{ .Site.Title }}",
  "url": "{{ .Site.BaseURL }}",
  "description": "{{ .Site.Params.description }}",
  "inLanguage": "bg-BG",
  "publisher": {
    "@type": "Organization",
    "name": "{{ .Site.Title }}",
    "logo": {
      "@type": "ImageObject",
      "url": "{{ .Site.Params.logo | absURL }}"
    }
  }
}
</script>
```

**3. Sitemap Configuration** (`hugo.toml`):
```toml
[sitemap]
  changefreq = "weekly"
  filename = "sitemap.xml"
  priority = 0.5
```

**4. Robots.txt**:
```
User-agent: *
Allow: /
Sitemap: https://gishe8.com/sitemap.xml
```

**SEO Best Practices**:
- Unique, descriptive titles (<60 chars)
- Compelling meta descriptions (<160 chars, Bulgarian)
- Proper heading hierarchy (single h1, logical h2-h6)
- Descriptive URLs (transliterated Bulgarian if needed)
- Alt text for all images
- Internal linking between pages

**Alternatives Considered**:
- Third-party SEO plugin → Rejected: Hugo templates are sufficient
- Microdata instead of JSON-LD → Rejected: JSON-LD is easier to maintain
- Skip structured data → Rejected: Violates Constitution Principle V

**References**:
- Schema.org WebSite: <https://schema.org/WebSite>
- Open Graph protocol: <https://ogp.me/>
- Twitter Cards guide: <https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards>
- Google Rich Results Test: <https://search.google.com/test/rich-results>

---

### 7. Satirical Bulgarian Content & Tone Guidelines

**Decision**: Establish content guidelines and example phrases for consistent satirical voice

**Rationale**:
- Tone consistency is constitutional requirement (Principle II)
- Satire about Bulgarian bureaucracy is core brand identity
- Guidelines ensure all contributors maintain voice

**Satirical Tone Elements**:

**1. Hero Tagline Options**:
- "Добре дошли в безкрайността на българската бюрокрация" (Welcome to the infinity of Bulgarian bureaucracy)
- "Пътуването през безбройните гишета на администрацията" (Journey through countless counters of administration)
- "Където Гише 8 винаги води към Гише 9, а Гише 9 - обратно към Гише 8" (Where Counter 8 always leads to Counter 9, and Counter 9 back to Counter 8)

**2. Placeholder Alt Text Examples**:
- "Човек чака на Гише 8 от 2007 година" (Person waiting at Counter 8 since 2007)
- "Формуляр 42-Б изисква формуляр 42-А, който не съществува" (Form 42-B requires Form 42-A, which doesn't exist)
- "Чиновникът на обедна почивка между 9:00 и 17:00" (Official at lunch break between 9:00 and 17:00)
- "Електронна услуга, достъпна само на хартия" (Electronic service, available only on paper)

**3. Article Title Style**:
- Absurdist observation + bureaucratic element
- Examples:
  - "Как да подадете молба за неподаване на молби"
  - "Новото електронно управление: 15 документа, 8 гишета, едно PDF"
  - "Гише 8 вече е виртуално, но опашката е истинска"

**4. Content Voice Rules**:
- Use Bulgarian language exclusively (bg-BG)
- Maintain deadpan, matter-of-fact delivery (humor through absurdity, not jokes)
- Reference real frustrations with bureaucracy (relatable)
- Exaggerate to absurdist levels while keeping "official" tone
- Avoid mean-spirited or personal attacks (satire of system, not individuals)

**5. Editorial Guidelines**:
- Articles should feel like they could be real bureaucratic announcements
- Use formal Bulgarian when describing absurd situations (contrast creates humor)
- Include fake official procedures, forms, or requirements
- Reference specific "Гише" (counter) numbers for recurring jokes

**Writing Checklist**:
- [ ] Text in Bulgarian (bg-BG)
- [ ] Satirical/absurdist tone maintained
- [ ] Bureaucracy theme central
- [ ] "Official" voice (formal language)
- [ ] Relatable frustration exaggerated to absurdity
- [ ] No personal attacks or mean-spirited content

**References**:
- The Onion (English satire reference)
- Bulgarian administrative terminology dictionary
- Real Bulgarian bureaucratic processes (for accurate parody)

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Static Site Generator | Hugo Extended | v0.135+ | Fast builds, built-in features, asset pipeline |
| CSS Framework | TailwindCSS | 3.x | Modern utility-first, customizable, small bundle |
| PostCSS Processor | PostCSS + Autoprefixer | Latest | Required for Tailwind, vendor prefixes |
| Typography | Inter font | Latest | Excellent Cyrillic support, modern, open-source |
| JavaScript | Vanilla ES6+ | Native | No framework needed, minimal bundle (<10KB) |
| Theme System | CSS Variables | Native | Instant switching, no dependencies |
| Storage | localStorage | Native | Theme preference persistence |
| Image Format | WebP with fallback | Hugo native | Best compression, Hugo built-in processing |
| Meta Framework | Open Graph + JSON-LD | Standards | SEO and social sharing |
| Accessibility | Semantic HTML5 + ARIA | Standards | WCAG 2.1 Level AA compliance |

**Total External Dependencies**:
- Hugo Extended (build tool)
- TailwindCSS (npm, dev dependency)
- PostCSS + Autoprefixer (npm, dev dependencies)
- Inter font (self-hosted or Google Fonts)

**Runtime Dependencies**: ZERO (all compiled by Hugo)

---

## Open Questions Resolved

1. ✅ **Hugo + Tailwind integration**: Use Hugo Pipes with PostCSS
2. ✅ **Cyrillic font choice**: Inter font (self-hosted or Google Fonts)
3. ✅ **Theme switching approach**: Vanilla JS + CSS variables + localStorage
4. ✅ **Performance optimization**: Multi-layered (Hugo Pipes, critical CSS, lazy loading, image optimization)
5. ✅ **Accessibility implementation**: Semantic HTML + ARIA + keyboard nav + contrast validation
6. ✅ **SEO strategy**: Open Graph + Twitter Cards + JSON-LD structured data
7. ✅ **Content tone guidelines**: Satirical, absurdist, Bulgarian bureaucracy theme

---

## Next Steps (Phase 1)

1. Generate `data-model.md` - Define content structure (Article, Theme, HomePage entities)
2. Generate `contracts/` - Not applicable for static site (no API contracts)
3. Generate `quickstart.md` - Development environment setup, build instructions
4. Update agent context files with technologies from this research
5. Re-evaluate Constitution Check after design phase

---

## References & Resources

- Hugo Documentation: <https://gohugo.io/documentation/>
- TailwindCSS Docs: <https://tailwindcss.com/docs>
- WCAG 2.1 Guidelines: <https://www.w3.org/WAI/WCAG21/quickref/>
- Core Web Vitals: <https://web.dev/vitals/>
- Schema.org: <https://schema.org/>
- Inter Font: <https://rsms.me/inter/>
- Bulgarian Language Code: bg-BG (ISO 639-1 + ISO 3166-1)
