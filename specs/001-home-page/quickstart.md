# Quickstart: Home Page Development

**Feature**: Home Page  
**Branch**: 001-home-page  
**Date**: 2025-10-12  
**Phase**: 1 - Design & Contracts

## Prerequisites

Before starting development, ensure you have the following installed:

### Required Software

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Hugo Extended | v0.135+ | Static site generator with SCSS/PostCSS support | `brew install hugo` (macOS) or download from [Hugo Releases](https://github.com/gohugoio/hugo/releases) |
| Node.js | 18+ | For npm packages (Tailwind, PostCSS) | `brew install node` or [nodejs.org](https://nodejs.org/) |
| npm | 9+ | Package manager (comes with Node.js) | Included with Node.js |
| Git | Any | Version control | `brew install git` or pre-installed on macOS |

### Verify Installation

```bash
# Check Hugo Extended
hugo version
# Should show: hugo v0.151.x extended ...

# Check Node.js
node --version
# Should show: v18.x.x or higher

# Check npm
npm --version
# Should show: 10.7.x or higher
```

**Important**: Make sure you have Hugo **Extended** edition (not standard Hugo). The Extended version is required for TailwindCSS/PostCSS processing.

---

## Initial Setup

### 1. Clone Repository & Switch to Feature Branch

```bash
# Clone repository (if not already cloned)
git clone https://github.com/kriniko/GisheNomerBezkrajnost.git
cd GisheNomerBezkrajnost

# Switch to feature branch
git checkout 001-home-page

# Or create if it doesn't exist
git checkout -b 001-home-page
```

### 2. Install Node Dependencies

```bash
# Install TailwindCSS and PostCSS
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest

# This creates package.json and node_modules/ (already in .gitignore)
```

### 3. Initialize TailwindCSS Configuration

```bash
# Generate tailwind.config.js
npx tailwindcss init

# Generate postcss.config.js
cat > postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF
```

### 4. Configure Tailwind for Hugo

Edit `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './themes/sarcastic/layouts/**/*.html',
    './content/**/*.md',
  ],
  darkMode: 'class', // Use class-based dark mode
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Custom colors for light/dark themes
        'light': {
          'bg-primary': '#ffffff',
          'bg-secondary': '#f5f5f7',
          'text-primary': '#1d1d1f',
          'text-secondary': '#6e6e73',
          'accent': '#0071e3',
        },
        'dark': {
          'bg-primary': '#1d1d1f',
          'bg-secondary': '#2c2c2e',
          'text-primary': '#f5f5f7',
          'text-secondary': '#a1a1a6',
          'accent': '#2997ff',
        },
      },
    },
  },
  plugins: [],
}
```

### 5. Setup Main CSS File

Create `themes/sarcastic/assets/css/main.css`:

```css
/* TailwindCSS directives */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom base styles */
@layer base {
  html {
    @apply scroll-smooth;
  }
  
  body {
    @apply font-sans antialiased;
  }
}

/* Custom component classes */
@layer components {
  .btn-primary {
    @apply px-6 py-3 rounded-lg font-semibold transition-colors duration-200;
  }
  
  .article-card {
    @apply rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden transition-shadow duration-200 hover:shadow-lg;
  }
}

/* Utility classes */
@layer utilities {
  .sr-only {
    @apply absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0;
    clip: rect(0, 0, 0, 0);
  }
}
```

---

## Development Workflow

### Running the Development Server

```bash
# Start Hugo development server
hugo server -D

# Or with specific flags
hugo server --disableFastRender --navigateToChanged

# Server will start at http://localhost:1313/
```

**Flags Explained**:
- `-D` or `--buildDrafts`: Include draft content
- `--disableFastRender`: Full rebuild on changes (useful for theme dev)
- `--navigateToChanged`: Auto-navigate to changed content in browser

**Live Reload**: Hugo automatically reloads the browser when you save changes to:
- Templates (`.html` files)
- Content (`.md` files)
- CSS (`.css` files via Hugo Pipes)
- JavaScript (`.js` files)

### File Structure for This Feature

```
GisheNomerBezkrajnost/
├── hugo.toml                 # MODIFY: Add theme params
├── package.json              # NEW: npm dependencies
├── tailwind.config.js        # NEW: Tailwind configuration
├── postcss.config.js         # NEW: PostCSS configuration
├── content/
│   ├── _index.md             # NEW: Home page content
│   └── article/              # ADD: Sample articles (5+)
│       ├── article-1.md
│       ├── article-2.md
│       └── ...
└── themes/sarcastic/
    ├── layouts/
    │   ├── index.html        # MODIFY: Home page layout
    │   ├── baseof.html       # MODIFY: Add theme support
    │   └── _partials/
    │       ├── head.html     # MODIFY: SEO meta tags
    │       ├── header.html   # MODIFY: Theme switcher
    │       ├── footer.html   # MODIFY: Update content
    │       ├── theme-switcher.html  # NEW: Theme control
    │       └── article-card.html    # NEW: Article preview
    ├── assets/
    │   ├── css/
    │   │   └── main.css      # NEW: Tailwind + custom CSS
    │   └── js/
    │       └── theme-switcher.js  # NEW: Theme logic
    └── static/
        └── fonts/            # OPTIONAL: Self-hosted fonts
```

### Creating Sample Articles

Use Hugo's archetype system to create sample articles:

```bash
# Create 5 sample articles
hugo new article/elektronno-gishe-iziskva-hartia.md
hugo new article/formular-42b-ne-sushtestvuva.md
hugo new article/gishe-8-raboti-samo-v-sreda.md
hugo new article/obedna-pochivka-9-do-17.md
hugo new article/nova-procedura-7-pechata.md

# Edit each file and set draft: false to publish
```

Sample article content (edit after creation):

```markdown
---
title: "Електронното гише изисква хартиена заявка"
date: 2025-10-12T10:00:00+02:00
draft: false
description: "Новата е-услуга обещава дигитализация, но първо трябва да подадете формуляр лично"
tags:
  - е-услуги
  - модернизация
  - абсурд
categories:
  - Електронно управление
---

## Революцията в администрацията

Днес беше обявена нова електронна услуга, която ще улесни живота на гражданите. Единственото изискване е да посетите Гише 8 лично и да подадете хартиена заявка за достъп до електронната система...
```

---

## Building for Production

### Production Build

```bash
# Build static site
hugo --minify

# Output will be in public/ directory
```

**Build Optimizations** (automatic with Hugo):
- CSS minification
- JS minification
- HTML minification (with `--minify`)
- Asset fingerprinting (cache busting)
- Image processing (WebP conversion, resizing)

### Testing Production Build Locally

```bash
# Build
hugo --minify

# Serve from public/ directory
cd public && python3 -m http.server 8000
# Or use: npx serve public

# Open http://localhost:8000
```

---

## Development Guidelines

### Theme Development Best Practices

1. **Always test in both themes** (light + dark)
   ```bash
   # Toggle theme in browser using theme switcher
   ```

2. **Test responsive layouts**
   - Use browser DevTools (Chrome/Firefox/Safari)
   - Test viewports: 320px (mobile), 375px (iPhone), 768px (tablet), 1024px (desktop), 1440px (large)

3. **Use Hugo's template debugging**
   ```go-html-template
   <!-- Debug variable -->
   {{ printf "%#v" . }}
   
   <!-- Check if variable exists -->
   {{ if .Params.title }}
     {{ .Params.title }}
   {{ else }}
     No title
   {{ end }}
   ```

4. **Validate HTML**
   - Build site: `hugo`
   - Validate: Visit [validator.w3.org](https://validator.w3.org/) and upload `public/index.html`

### CSS Development

1. **Use Tailwind utility classes first**
   ```html
   <div class="max-w-4xl mx-auto px-4 py-8">
     <h1 class="text-4xl font-bold text-gray-900 dark:text-gray-100">
       Гише безкрайност
     </h1>
   </div>
   ```

2. **Extract repeated patterns to `@layer components`**
   ```css
   @layer components {
     .hero-title {
       @apply text-5xl md:text-6xl font-black tracking-tight;
     }
   }
   ```

3. **Theme-specific styles using dark mode**
   ```html
   <div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
     Content
   </div>
   ```

### JavaScript Development

1. **Keep it minimal** - Target <10KB total
2. **Use vanilla ES6+** - No frameworks
3. **Progressive enhancement** - Site works without JS
4. **Use `defer` attribute**
   ```html
   <script src="{{ $js.RelPermalink }}" defer></script>
   ```

---

## Testing Checklist

### Functional Testing

- [ ] Home page loads successfully at `/`
- [ ] 5 most recent articles displayed (or all if <5)
- [ ] Article titles, dates, and summaries visible
- [ ] Clicking article navigates to article page
- [ ] Theme switcher visible in header
- [ ] Light theme works
- [ ] Dark theme works
- [ ] System theme respects OS preference
- [ ] Theme preference persists after page reload

### Responsive Testing

- [ ] Layout works on 320px width (iPhone SE)
- [ ] Layout works on 375px width (iPhone 12/13)
- [ ] Layout works on 768px width (iPad)
- [ ] Layout works on 1024px+ width (desktop)
- [ ] No horizontal scroll on any viewport
- [ ] Text is readable (min 16px on mobile)
- [ ] Touch targets are ≥44x44px

### Performance Testing

```bash
# Build for production
hugo --minify

# Serve locally
cd public && python3 -m http.server 8000

# Run Lighthouse in Chrome DevTools
# Target: 90+ in all categories
```

- [ ] Lighthouse Performance Score ≥90
- [ ] Lighthouse Accessibility Score ≥90
- [ ] Lighthouse Best Practices Score ≥90
- [ ] Lighthouse SEO Score ≥90
- [ ] Core Web Vitals in "Good" range (green)
- [ ] Total page weight <500KB (excl. images)

### Accessibility Testing

- [ ] All images have alt text
- [ ] Keyboard navigation works (tab through page)
- [ ] Focus indicators visible
- [ ] Color contrast passes WCAG AA (use DevTools)
- [ ] Screen reader test (NVDA on Windows or VoiceOver on macOS)
- [ ] Heading hierarchy is logical (h1 → h2 → h3)
- [ ] ARIA labels present where needed

### SEO Testing

- [ ] Meta description present in `<head>`
- [ ] Open Graph tags present
- [ ] Twitter Card tags present
- [ ] JSON-LD structured data present
- [ ] Canonical URL specified
- [ ] Language meta tag set to bg-BG
- [ ] Title tag unique and descriptive

### Browser Testing

Test in at least:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

---

## Common Issues & Solutions

### Issue: Hugo not found or wrong version

**Solution**:
```bash
# Check version
hugo version

# If not Extended, reinstall
brew uninstall hugo
brew install hugo
```

### Issue: TailwindCSS not processing

**Solution**:
```bash
# Check postcss.config.js exists
ls postcss.config.js

# Restart Hugo server
# Kill server (Ctrl+C) and run again
hugo server -D
```

### Issue: Theme switcher not working

**Solution**:
1. Check browser console for JavaScript errors
2. Verify `theme-switcher.js` is loaded in network tab
3. Check localStorage in DevTools Application tab

### Issue: Images not loading

**Solution**:
```bash
# Check image path in content
# Should be relative to content file or in static/

# For page bundle images:
content/article/my-article/
├── index.md
└── featured.jpg  # Access as {{ .Resources.Get "featured.jpg" }}

# For static images:
static/images/logo.png  # Access as /images/logo.png
```

### Issue: Fonts not loading

**Solution**:
1. Check network tab for 404 errors
2. Verify font files are in `themes/sarcastic/static/fonts/`
3. Check @font-face paths in CSS
4. Use relative paths: `/fonts/Inter-Regular.woff2`

---

## Useful Commands Reference

```bash
# Development server
hugo server -D                          # With drafts
hugo server --disableFastRender         # Full rebuilds
hugo server --navigateToChanged         # Auto-navigate

# Content creation
hugo new article/my-article.md          # New article
hugo new content/_index.md              # New index page

# Production build
hugo --minify                           # Minified build
hugo --minify --gc                      # With garbage collection

# Cleaning
rm -rf public/ resources/               # Clean build artifacts
hugo mod clean                          # Clean module cache (if using modules)

# Git workflow
git status                              # Check changes
git add .                               # Stage all changes
git commit -m "feat: implement home page"
git push origin 001-home-page           # Push to remote
```

---

## Next Steps

After completing the quickstart setup:

1. ✅ Verify all prerequisites installed
2. ✅ Run `hugo server -D` and confirm it works
3. ✅ Create 5 sample articles
4. 📋 Move to `tasks.md` for implementation steps
5. 🚀 Start implementing tasks from Phase 1 (Setup)

---

## Resources

- **Hugo Documentation**: <https://gohugo.io/documentation/>
- **TailwindCSS Docs**: <https://tailwindcss.com/docs>
- **Lighthouse CLI**: `npm install -g lighthouse`
- **HTML Validator**: <https://validator.w3.org/>
- **Contrast Checker**: <https://webaim.org/resources/contrastchecker/>
- **Screen Reader**: NVDA (Windows) or VoiceOver (macOS)

---

## Support

For issues or questions about this feature:
1. Check this quickstart guide
2. Review `research.md` for technical decisions
3. Check `data-model.md` for content structure
4. Consult `.specify/memory/constitution.md` for project principles
