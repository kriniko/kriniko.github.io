# Feature Specification: Home Page

**Feature Branch**: `001-home-page`  
**Created**: 2025-10-12  
**Status**: Draft  
**Input**: User description: "Create a website home page for GisheBezkrajnost (гише безкрайност or гише8) - counter infinity denoting the infinite number of counters one needs to visit in a bureaucratic system. Create a funny and sarcastic modern web page linking to the last 5 articles. Use modern fonts and style. Where images are needed use a placeholder with alt text."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time Visitor Discovery (Priority: P1) 🎯 MVP

A Bulgarian reader lands on the home page through social media or search and immediately understands the satirical nature of the site, sees the latest articles, and is entertained by the absurdist bureaucracy theme.

**Why this priority**: First impressions determine whether visitors stay and explore. The home page must instantly communicate the site's unique satirical voice about Bulgarian bureaucracy.

**Independent Test**: Can be fully tested by loading the home page in a browser and verifying that the hero section, tagline, and article previews are visible and convey the satirical theme.

**Acceptance Scenarios**:

1. **Given** a first-time visitor opens gishe8.com, **When** the page loads, **Then** they see a hero section with the site name "Гише безкрайност" (or "Гише8"), a humorous tagline about bureaucratic infinity, and understand it's a satirical site
2. **Given** the home page is loaded, **When** the visitor scrolls, **Then** they see the 5 most recent articles with titles, publication dates, and short summaries in satirical tone
3. **Given** a visitor with slow 3G connection, **When** the home page loads, **Then** it renders in under 2 seconds with all critical content visible

---

### User Story 2 - Article Discovery & Navigation (Priority: P2)

Returning visitors can quickly find and access the latest satirical articles about Bulgarian bureaucracy.

**Why this priority**: Content discovery is the primary purpose of the home page. Easy navigation keeps visitors engaged.

**Independent Test**: Click on any article preview and verify navigation to the full article works correctly.

**Acceptance Scenarios**:

1. **Given** the home page displays 5 recent articles, **When** visitor clicks an article title or preview, **Then** they navigate to the full article page
2. **Given** visitor is on the home page, **When** they hover over article previews, **Then** visual feedback indicates interactivity (subtle hover effects)
3. **Given** articles have featured images, **When** the page loads, **Then** placeholder images with satirical alt text are displayed (e.g., "Човек чака на Гише 8 от 2007 година")

---

### User Story 3 - Theme Switching Experience (Priority: P2)

Visitors can switch between light, dark, and system themes for comfortable reading at any time of day.

**Why this priority**: Theme support enhances accessibility and user preference, aligning with modern web standards.

**Independent Test**: Use the theme switcher control to change between light/dark/system modes and verify instant visual changes without page reload.

**Acceptance Scenarios**:

1. **Given** visitor is on the home page, **When** they first load the site, **Then** the theme matches their system preference (default: system)
2. **Given** the theme switcher is visible in the header, **When** visitor clicks to change theme (light/dark/system), **Then** the page instantly switches themes without reload and saves preference
3. **Given** theme is changed, **When** visitor returns to the site, **Then** their theme preference persists

---

### User Story 4 - Mobile-Optimized Experience (Priority: P1) 🎯 MVP

Mobile users with potentially unstable connections get a fast, fully functional, and visually appealing home page.

**Why this priority**: Many Bulgarian users access content via mobile with varying connection quality. Mobile-first is a core principle.

**Independent Test**: Open home page on mobile device/viewport and verify layout adapts, navigation works, and performance targets are met.

**Acceptance Scenarios**:

1. **Given** visitor opens the home page on mobile, **When** the page loads, **Then** layout adapts responsively with readable text, touch-friendly navigation, and no horizontal scroll
2. **Given** mobile viewport is 375px wide, **When** viewing article previews, **Then** they stack vertically with appropriate spacing
3. **Given** mobile user with slow connection, **When** page loads, **Then** Core Web Vitals meet targets (LCP <2.5s, FID <100ms, CLS <0.1)

---

### User Story 5 - SEO & Social Sharing (Priority: P3)

The home page is optimized for search engines and social media sharing to drive traffic.

**Why this priority**: Essential for growth and monetization, but can be implemented after core functionality works.

**Independent Test**: Validate Open Graph tags and JSON-LD structured data using testing tools (Facebook debugger, Google Rich Results Test).

**Acceptance Scenarios**:

1. **Given** the home page is shared on social media, **When** the link is posted, **Then** rich preview shows site name, tagline, and featured image with proper Bulgarian text
2. **Given** search engines index the home page, **When** viewing page source, **Then** proper meta tags, JSON-LD structured data for Organization/Website, and semantic HTML are present
3. **Given** visitor uses screen reader, **When** navigating the home page, **Then** all content is accessible with proper ARIA labels and semantic structure

---

### Edge Cases

- What happens when fewer than 5 articles exist? **Display all available articles, maintain layout without empty spaces**
- How does the site handle very long article titles in Bulgarian? **Truncate with ellipsis after 80 characters, show full title on hover**
- What if images fail to load? **Show styled placeholder with meaningful alt text and icon**
- How does theme switcher work for visitors with JavaScript disabled? **Default to light theme with proper CSS, show message encouraging JS for full features**
- What happens when site name is displayed on very narrow mobile screens (320px)? **Use abbreviated version "Гише8" for ultra-narrow viewports**

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Home page MUST display the site name "Гише безкрайност" (or "Гише8") prominently in the hero section
- **FR-002**: Home page MUST include a satirical tagline explaining the bureaucracy theme (e.g., "Пътуването през безкрайните гишета на българската бюрокрация")
- **FR-003**: Home page MUST display the 5 most recent published articles sorted by date (newest first)
- **FR-004**: Each article preview MUST show: title, publication date, excerpt/summary (100-150 chars), featured image placeholder
- **FR-005**: Home page MUST be fully responsive from 320px to 4K screens
- **FR-006**: Theme switcher MUST be visible and functional (light/dark/system modes)
- **FR-007**: Theme preference MUST persist across sessions using localStorage
- **FR-008**: All text content MUST be in Bulgarian language (bg-BG)
- **FR-009**: Satirical tone MUST be maintained in all copy (hero text, article summaries)
- **FR-010**: Home page MUST include Open Graph and Twitter Card metadata
- **FR-011**: Home page MUST include JSON-LD structured data for Organization and WebSite
- **FR-012**: Navigation MUST include keyboard support (tab navigation, enter to activate)
- **FR-013**: Home page MUST include a header with site logo/name and navigation menu
- **FR-014**: Home page MUST include a footer with copyright, social links placeholder, and theme attribution
- **FR-015**: All interactive elements MUST have focus states for accessibility

### Key Entities *(include if feature involves data)*

- **Article**: Represents satirical content
  - Title (string, Bulgarian)
  - Date (datetime)
  - Summary/Excerpt (string, 100-150 chars)
  - Featured Image (optional, with fallback to placeholder)
  - Permalink (URL)
  
- **Theme Preference**: User's color scheme choice
  - Mode (enum: light, dark, system)
  - Stored in localStorage

### Design & Style Requirements

- **DR-001**: Typography MUST use modern fonts with full Cyrillic support (e.g., Inter, SF Pro, or similar)
- **DR-002**: Apple-style design patterns MUST be applied: spacious layouts, ample white space, large readable text
- **DR-003**: Color scheme MUST support three themes with appropriate contrast ratios (WCAG AA)
- **DR-004**: Hero section MUST be visually distinct with large typography and subtle background
- **DR-005**: Article cards MUST have consistent styling: bordered/shadowed containers, hover effects
- **DR-006**: TailwindCSS MUST be used for all styling via Hugo asset pipeline
- **DR-007**: Font sizes MUST scale appropriately for mobile (min 16px for body text to prevent zoom)
- **DR-008**: Spacing MUST follow consistent scale (e.g., 4px, 8px, 16px, 24px, 32px, 48px, 64px)
- **DR-009**: Button/link hover states MUST include subtle transitions (200-300ms)
- **DR-010**: Placeholder images MUST have distinctive satirical Bulgarian alt text

### Performance Requirements

- **PR-001**: Home page MUST load in under 2 seconds on 3G connection
- **PR-002**: Lighthouse Performance score MUST be 90+
- **PR-003**: Core Web Vitals MUST meet "Good" thresholds:
  - LCP (Largest Contentful Paint) <2.5s
  - FID (First Input Delay) <100ms
  - CLS (Cumulative Layout Shift) <0.1
- **PR-004**: Total page weight MUST be <500KB (excluding images)
- **PR-005**: CSS MUST be minified and inlined for critical styles
- **PR-006**: JavaScript MUST be minimal (<10KB minified) and non-blocking
- **PR-007**: Images MUST use lazy loading (except hero section)
- **PR-008**: Fonts MUST use font-display: swap to prevent render blocking

### Accessibility Requirements

- **AR-001**: Home page MUST meet WCAG 2.1 Level AA standards
- **AR-002**: Color contrast ratios MUST be at least 4.5:1 for normal text, 3:1 for large text
- **AR-003**: All images MUST have descriptive alt text in Bulgarian
- **AR-004**: Semantic HTML5 elements MUST be used (header, nav, main, article, footer)
- **AR-005**: ARIA labels MUST be provided where semantic HTML is insufficient
- **AR-006**: Keyboard navigation MUST work throughout (tab order logical)
- **AR-007**: Focus indicators MUST be clearly visible
- **AR-008**: Screen reader testing MUST pass with NVDA/VoiceOver

### SEO Requirements

- **SR-001**: Title tag MUST be descriptive and include site name
- **SR-002**: Meta description MUST be compelling and under 160 characters (Bulgarian)
- **SR-003**: Open Graph tags MUST include: og:title, og:description, og:image, og:url, og:type
- **SR-004**: Twitter Card tags MUST be included (summary_large_image)
- **SR-005**: Canonical URL MUST be specified
- **SR-006**: Language meta tag MUST be set to bg-BG
- **SR-007**: JSON-LD structured data MUST include Organization and WebSite schemas
- **SR-008**: Heading hierarchy MUST be logical (single h1, proper h2-h6 nesting)

## Non-Requirements

- Article creation/editing interface (separate feature)
- User authentication or commenting system
- Article filtering or search (future feature)
- Newsletter subscription (future monetization feature)
- Ad placement implementation (future, but zones should be planned)
- Analytics integration (future)
- More than 5 articles on home page
- Pagination on home page (link to article archive instead)

## Technical Approach

### Hugo Template Structure

```
themes/sarcastic/layouts/
├── index.html (home page layout - replaces home.html)
├── baseof.html (base template - enhanced)
└── _partials/
    ├── head.html (meta tags, styles)
    ├── header.html (logo, nav, theme switcher)
    ├── footer.html (copyright, social links)
    ├── theme-switcher.html (light/dark/system control)
    └── article-card.html (reusable article preview)
```

### CSS Architecture (TailwindCSS)

```
themes/sarcastic/assets/css/
├── main.css (Tailwind imports + custom utilities)
└── themes/
    ├── light.css (light theme variables)
    └── dark.css (dark theme variables)
```

### JavaScript Components

```
themes/sarcastic/assets/js/
└── theme-switcher.js (vanilla JS for theme management, ~50 lines)
```

### Content Structure

```
content/
├── _index.md (home page content/frontmatter)
└── article/
    └── [articles].md (5+ articles needed for testing)
```

## Open Questions

1. Should the hero section include a large illustration/graphic or keep it text-only with subtle background?
   - **Recommendation**: Text-only with subtle CSS gradient for performance
   
2. What specific modern font should we use for Cyrillic?
   - **Options**: Inter (Google Fonts), SF Pro Display (if self-hosted), Roboto
   - **Recommendation**: Inter - excellent Cyrillic support, modern, open-source
   
3. Should article excerpts be auto-generated or manually written in frontmatter?
   - **Recommendation**: Manual in frontmatter for better control, fallback to Hugo's .Summary
   
4. What's the exact Bulgarian tagline/slogan for the hero?
   - **Proposal**: "Добре дошли в безкрайността на българската бюрокрация" or "Пътуването през безбройните гишета на българската администрация"
   
5. Should we include article categories/tags on the home page previews?
   - **Recommendation**: Yes, add 1-2 tags per article for better content discovery

## Success Criteria

- [ ] Home page loads in <2s on 3G
- [ ] Lighthouse scores all 90+ (Performance, Accessibility, Best Practices, SEO)
- [ ] All three theme modes work instantly without flicker
- [ ] Mobile layout is fully functional on 375px viewport
- [ ] Screen reader can navigate entire page logically
- [ ] Article previews are clickable and navigate correctly
- [ ] Bulgarian text renders correctly in all themes
- [ ] Page validates as HTML5
- [ ] Open Graph preview looks correct on Facebook/Twitter
- [ ] No console errors in browser
- [ ] Theme preference persists across sessions

## Mockup/Wireframe Description

Since we can't attach images, here's a text description:

### Desktop Layout (1200px+)

```
┌────────────────────────────────────────────────────┐
│ HEADER: [Гише∞] [nav links]        [🌙 Theme]    │
├────────────────────────────────────────────────────┤
│                                                     │
│              HERO SECTION (centered)                │
│         Гише безкрайност (Гише8)                   │
│    [Satirical tagline about bureaucracy]           │
│           [Placeholder graphic area]                │
│                                                     │
├────────────────────────────────────────────────────┤
│                                                     │
│           Latest Articles (Последни статии)        │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │ [IMG]        │  │ [IMG]        │  │ [IMG]   │ │
│  │ Article 1    │  │ Article 2    │  │ Article │ │
│  │ Date         │  │ Date         │  │ Date    │ │
│  │ Summary...   │  │ Summary...   │  │ Summary │ │
│  └──────────────┘  └──────────────┘  └─────────┘ │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ [IMG]        │  │ [IMG]        │               │
│  │ Article 4    │  │ Article 5    │               │
│  │ Date         │  │ Date         │               │
│  │ Summary...   │  │ Summary...   │               │
│  └──────────────┘  └──────────────┘               │
│                                                     │
├────────────────────────────────────────────────────┤
│ FOOTER: © 2025 | [Social] | [Links]               │
└────────────────────────────────────────────────────┘
```

### Mobile Layout (375px)

```
┌─────────────────────┐
│ [☰] Гише8  [🌙]    │
├─────────────────────┤
│                     │
│    Гише безкрайност │
│    [Tagline]        │
│                     │
├─────────────────────┤
│ Последни статии     │
│                     │
│ ┌─────────────────┐ │
│ │ [IMG]           │ │
│ │ Article Title 1 │ │
│ │ Date            │ │
│ │ Summary...      │ │
│ └─────────────────┘ │
│                     │
│ ┌─────────────────┐ │
│ │ [IMG]           │ │
│ │ Article Title 2 │ │
│ │ Date            │ │
│ │ Summary...      │ │
│ └─────────────────┘ │
│                     │
│ [... 3 more cards]  │
│                     │
├─────────────────────┤
│ © 2025 | Links      │
└─────────────────────┘
```

## Dependencies

- Hugo Extended (latest stable) - for TailwindCSS processing
- TailwindCSS (via Hugo Pipes) - styling framework
- Inter font (Google Fonts or self-hosted) - Cyrillic typography
- No JavaScript frameworks required (vanilla JS only)

## References

- Constitution: `.specify/memory/constitution.md`
- Hugo Documentation: https://gohugo.io/documentation/
- TailwindCSS Docs: https://tailwindcss.com/docs
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- Core Web Vitals: https://web.dev/vitals/
