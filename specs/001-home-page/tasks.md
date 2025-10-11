# Tasks: Home Page

**Feature**: Home Page  
**Branch**: `001-home-page` | **Date**: 2025-10-12  
**Input**: Design documents from `/specs/001-home-page/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: This feature does not include automated tests. Testing will be manual (browser testing, Lighthouse, accessibility tools).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

**Hugo Static Site**: All paths relative to repository root
- Theme files: `themes/sarcastic/`
- Content files: `content/`
- Config: `hugo.toml`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic dependencies needed by all stories

- [ ] T001 [P] Install Hugo Extended (verify with `hugo version`, must show "extended")
- [ ] T002 [P] Initialize npm project and install dependencies: `npm install -D tailwindcss@latest postcss@latest autoprefixer@latest`
- [ ] T003 Create `tailwind.config.js` with content paths and Cyrillic font configuration (Inter font stack)
- [ ] T004 Create `postcss.config.js` with TailwindCSS and Autoprefixer plugins
- [ ] T005 Create `.gitignore` entries for `node_modules/`, `public/`, `resources/`

**Checkpoint**: Dependencies installed, build tools configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Configure `hugo.toml`: Set baseURL, languageCode (bg-BG), title ("Гише безкрайност"), theme ("sarcastic")
- [ ] T007 [P] Create main CSS file at `themes/sarcastic/assets/css/main.css` with Tailwind directives (@tailwind base, components, utilities)
- [ ] T008 [P] Create base layout template at `themes/sarcastic/layouts/baseof.html` with HTML5 structure, language (bg), and theme support
- [ ] T009 Create head partial at `themes/sarcastic/layouts/_partials/head.html` with meta tags, CSS loading via Hugo Pipes (PostCSS, minify, fingerprint)
- [ ] T010 [P] Add custom Tailwind utilities to `main.css`: `.sr-only` for screen reader text, `.article-card` component class
- [ ] T011 [P] Create theme CSS variables files:
  - `themes/sarcastic/assets/css/themes/light.css` (light theme variables)
  - `themes/sarcastic/assets/css/themes/dark.css` (dark theme variables)
- [ ] T012 Import theme CSS files in `main.css` and setup `:root[data-theme="light"]` and `:root[data-theme="dark"]` selectors
- [ ] T013 [P] Add `@media (prefers-color-scheme: dark)` for system theme default in `main.css`
- [ ] T014 Update `hugo.toml` params section: defaultTheme="system", homeArticleCount=5, excerptLength=150
- [ ] T015 Create header partial at `themes/sarcastic/layouts/_partials/header.html` with site name and nav placeholder
- [ ] T016 Create footer partial at `themes/sarcastic/layouts/_partials/footer.html` with copyright and links placeholder

**Checkpoint**: Foundation ready - Hugo builds successfully, base template renders, theme CSS loaded

---

## Phase 3: User Story 1 - First-Time Visitor Discovery (Priority: P1) 🎯 MVP

**Goal**: Display hero section with site name/tagline and 5 most recent articles with satirical tone

**Independent Test**: Load home page in browser, verify hero section visible with "Гише безкрайност" title and tagline, confirm 5 article previews displayed with titles, dates, summaries

### Implementation for User Story 1

- [ ] T017 [US1] Create home page content file at `content/_index.md` with frontmatter: title, description, tagline (Bulgarian satirical text)
- [ ] T018 [US1] Create home page layout at `themes/sarcastic/layouts/index.html` with hero section displaying `.Site.Title` and `.Params.tagline`
- [ ] T019 [US1] Add article query logic to `index.html`: filter by type "article", exclude drafts, sort by date, limit to 5 (or `.Site.Params.homeArticleCount`)
- [ ] T020 [US1] Create article card partial at `themes/sarcastic/layouts/_partials/article-card.html` to display article title, date, description
- [ ] T021 [US1] Style hero section in `main.css` with large typography (text-5xl md:text-6xl), centered layout, spacious padding
- [ ] T022 [US1] Style article cards in `main.css`: bordered containers, rounded corners, hover effects, responsive grid (1 col mobile, 2-3 cols desktop)
- [ ] T023 [US1] Create 5 sample articles in `content/article/` with Bulgarian satirical content, proper frontmatter (title, date, description, draft: false)
- [ ] T024 [US1] Add placeholder image support to article card partial: check for `featured_image` param, display with satirical Bulgarian alt text
- [ ] T025 [US1] Format article dates in Bulgarian locale in article card partial using Hugo's date formatting
- [ ] T026 [US1] Test responsive layout on mobile (320px, 375px) and desktop (1024px+): verify no horizontal scroll, readable text, proper spacing

**Checkpoint**: User Story 1 complete - Hero section displays, 5 articles visible with satirical content, responsive layout works

---

## Phase 4: User Story 4 - Mobile-Optimized Experience (Priority: P1) 🎯 MVP

**Goal**: Ensure home page is fully responsive, fast-loading, and mobile-friendly

**Independent Test**: Open on mobile device/viewport (375px), verify layout adapts, text readable (min 16px), no horizontal scroll, Core Web Vitals in "Good" range

### Implementation for User Story 4

- [ ] T027 [US4] Configure responsive typography in `tailwind.config.js`: base 16px mobile, scale up for desktop
- [ ] T028 [US4] Add responsive breakpoints to article grid: single column <768px, 2 columns 768-1024px, 3 columns >1024px
- [ ] T029 [US4] Implement mobile navigation: hamburger menu for narrow viewports, horizontal menu for desktop (update header partial)
- [ ] T030 [US4] Add touch-friendly sizing: min 44x44px tap targets for buttons and links (Tailwind classes: `min-h-11 min-w-11`)
- [ ] T031 [US4] Optimize images: add `loading="lazy"` to article card images, specify width/height to prevent CLS
- [ ] T032 [US4] Inline critical CSS in head partial: extract above-the-fold styles for hero section, inline in `<style>` tag
- [ ] T033 [US4] Add font-display: swap to font loading in CSS to prevent FOIT (Flash of Invisible Text)
- [ ] T034 [US4] Configure Hugo asset minification: update head partial to use `| minify` and `| fingerprint` in production
- [ ] T035 [US4] Test viewport scaling: add `<meta name="viewport" content="width=device-width, initial-scale=1.0">` in head partial
- [ ] T036 [US4] Run Lighthouse audit: verify Performance 90+, LCP <2.5s, FID <100ms, CLS <0.1
- [ ] T037 [US4] Test on real mobile devices (iOS Safari, Chrome Android) or use Chrome DevTools device emulation

**Checkpoint**: User Story 4 complete - Mobile layout perfect, performance targets met, Lighthouse score 90+

---

## Phase 5: User Story 2 - Article Discovery & Navigation (Priority: P2)

**Goal**: Article previews are clickable, navigation works, hover effects present

**Independent Test**: Hover over article cards (verify visual feedback), click article title/card (verify navigation to article page)

### Implementation for User Story 2

- [ ] T038 [US2] Make article card clickable: wrap entire card in `<a>` tag with `href="{{ .Permalink }}"` in article-card partial
- [ ] T039 [US2] Add hover effects to article cards: scale transform, shadow increase, border color change (use Tailwind `hover:` utilities)
- [ ] T040 [US2] Add transition duration to article cards: `transition-all duration-200` for smooth hover animation
- [ ] T041 [US2] Style article title as link: underline on hover, color change, visited state styling
- [ ] T042 [US2] Add focus states for keyboard navigation: visible outline on article card focus (`focus:ring-2 focus:ring-offset-2`)
- [ ] T043 [US2] Create article page layout at `themes/sarcastic/layouts/article/single.html` (basic layout for navigation target)
- [ ] T044 [US2] Test article navigation: click cards, verify URL changes, article page loads
- [ ] T045 [US2] Test keyboard navigation: tab through article cards, press Enter to navigate

**Checkpoint**: User Story 2 complete - Articles clickable, hover effects work, navigation functional

---

## Phase 6: User Story 3 - Theme Switching Experience (Priority: P2)

**Goal**: Light/dark/system theme modes work, instant switching, preference persists

**Independent Test**: Use theme switcher buttons, verify instant visual change without reload, refresh page and verify preference persists

### Implementation for User Story 3

- [ ] T046 [US3] Create theme switcher JavaScript at `themes/sarcastic/assets/js/theme-switcher.js`: read localStorage, apply theme to `:root[data-theme]`, handle button clicks
- [ ] T047 [US3] Add theme initialization script inline in head partial (before CSS): immediately apply saved theme to prevent flash of wrong theme
- [ ] T048 [US3] Create theme switcher UI partial at `themes/sarcastic/layouts/_partials/theme-switcher.html`: 3 buttons for light/dark/system with icons
- [ ] T049 [US3] Add theme switcher to header partial: include `{{ partial "theme-switcher.html" . }}`
- [ ] T050 [US3] Style theme switcher buttons: icon-only design, circular buttons, active state indication, ARIA labels in Bulgarian
- [ ] T051 [US3] Implement localStorage logic in JS: `getItem('gishe-theme')`, `setItem('gishe-theme', theme)`, default to 'system'
- [ ] T052 [US3] Add event listeners in JS: listen for button clicks with `data-theme-toggle` attribute, update theme and save to localStorage
- [ ] T053 [US3] Update button visual states in JS: add/remove active classes, update `aria-pressed` attributes
- [ ] T054 [US3] Test theme switching: click light/dark/system buttons, verify instant change, no page flicker, localStorage updated
- [ ] T055 [US3] Test theme persistence: change theme, reload page, verify theme maintained
- [ ] T056 [US3] Test system theme: set OS to dark mode, verify site respects preference when theme="system"
- [ ] T057 [US3] Add fallback for no-JS: show message encouraging JavaScript, default to light theme via CSS

**Checkpoint**: User Story 3 complete - All 3 theme modes work, switching instant, preferences persist

---

## Phase 7: User Story 5 - SEO & Social Sharing (Priority: P3)

**Goal**: Home page optimized for search engines and social media with proper metadata

**Independent Test**: Validate Open Graph tags with Facebook debugger, test JSON-LD with Google Rich Results Test, verify accessibility with screen reader

### Implementation for User Story 5

- [ ] T058 [US5] Add Open Graph meta tags to head partial: og:title, og:description, og:type (website), og:url, og:locale (bg_BG), og:site_name, og:image
- [ ] T059 [US5] Add Twitter Card meta tags to head partial: twitter:card (summary_large_image), twitter:title, twitter:description, twitter:image
- [ ] T060 [US5] Add basic SEO meta tags: description, language (bg-BG), canonical URL, viewport (if not already added)
- [ ] T061 [US5] Create JSON-LD structured data partial at `themes/sarcastic/layouts/_partials/structured-data.html` for WebSite and Organization schemas
- [ ] T062 [US5] Include structured data partial in baseof.html: `{{ partial "structured-data.html" . }}`
- [ ] T063 [US5] Configure sitemap in `hugo.toml`: changefreq, priority, filename (sitemap.xml)
- [ ] T064 [US5] Add semantic HTML5 elements: `<header>`, `<main>`, `<article>`, `<footer>`, `<nav>` with proper hierarchy
- [ ] T065 [US5] Add ARIA labels for accessibility: navigation (`aria-label="Главно меню"`), article list (`aria-labelledby`), theme switcher (`aria-label` in Bulgarian)
- [ ] T066 [US5] Add skip link for keyboard navigation: "Към основното съдържание" link at top of body, styled with `.sr-only` and `:focus` visible
- [ ] T067 [US5] Verify heading hierarchy: single `<h1>` (hero title), `<h2>` for section headings, `<h3>` for article titles
- [ ] T068 [US5] Test color contrast: use WebAIM contrast checker, verify all text meets WCAG AA (4.5:1 for normal, 3:1 for large)
- [ ] T069 [US5] Test with screen reader: NVDA (Windows) or VoiceOver (macOS), verify logical reading order, all elements announced
- [ ] T070 [US5] Validate Open Graph: use Facebook Sharing Debugger (https://developers.facebook.com/tools/debug/)
- [ ] T071 [US5] Validate JSON-LD: use Google Rich Results Test (https://search.google.com/test/rich-results)
- [ ] T072 [US5] Validate HTML5: use W3C Validator (https://validator.w3.org/), fix any errors

**Checkpoint**: User Story 5 complete - SEO metadata present, social sharing works, accessibility verified

---

## Phase 8: Polish & Integration

**Purpose**: Cross-cutting concerns, final optimizations, and production readiness

- [ ] T073 [P] Download and self-host Inter font: add WOFF2 files to `themes/sarcastic/static/fonts/`, update CSS with `@font-face`
- [ ] T074 [P] Add preload hints for critical fonts in head partial: `<link rel="preload" href="/fonts/Inter-Regular.woff2" as="font" type="font/woff2" crossorigin>`
- [ ] T075 Create placeholder image for articles: SVG with satirical Bulgarian text, add to `themes/sarcastic/static/images/placeholder.svg`
- [ ] T076 Update article card partial: use placeholder image if `featured_image` not specified
- [ ] T077 Add error handling for missing articles: display message if <5 articles available, maintain layout
- [ ] T078 Configure production build in `hugo.toml`: `[minify]` settings for HTML, CSS, JS
- [ ] T079 Test full build: run `hugo --minify`, verify `public/` directory generated correctly
- [ ] T080 Add `robots.txt` to `static/`: allow all, specify sitemap location
- [ ] T081 Verify all Bulgarian text: check hero, tagline, article samples, alt text, ARIA labels for consistency and tone
- [ ] T082 Cross-browser testing: test in Chrome, Firefox, Safari, Edge (latest versions)
- [ ] T083 Final Lighthouse audit: run on production build, verify all scores 90+, Core Web Vitals green
- [ ] T084 Performance budget check: verify page weight <500KB (excl. images), JS <10KB
- [ ] T085 Accessibility final check: complete WCAG 2.1 Level AA checklist, test keyboard navigation thoroughly

**Checkpoint**: All polish complete - Production ready, all tests passing, performance targets met

---

## Phase 9: Documentation & Cleanup

**Purpose**: Update documentation and prepare for deployment

- [ ] T086 Update README.md with build instructions, development commands, deployment notes
- [ ] T087 Document Bulgarian content guidelines: tone, style examples, satirical tagline options (reference research.md)
- [ ] T088 Create content authoring guide: how to add new articles, frontmatter fields, Hugo archetype usage
- [ ] T089 Clean up temporary files: remove sample test articles if needed, verify .gitignore coverage
- [ ] T090 Final git commit: stage all changes, commit with message "feat: implement home page with 5 user stories"

**Checkpoint**: Documentation complete, ready for deployment

---

## Dependencies & Execution Order

### User Story Completion Order

```
Prerequisites (must complete first):
├─ Phase 1: Setup
└─ Phase 2: Foundational

MVP (can start after prerequisites):
├─ Phase 3: User Story 1 (First-Time Visitor) ← Start here for MVP
└─ Phase 4: User Story 4 (Mobile-Optimized) ← Essential for MVP

Post-MVP (can implement in any order):
├─ Phase 5: User Story 2 (Article Navigation)
├─ Phase 6: User Story 3 (Theme Switching)
└─ Phase 7: User Story 5 (SEO & Social Sharing)

Final Touches:
├─ Phase 8: Polish & Integration
└─ Phase 9: Documentation
```

### MVP Scope (Recommended First Release)

**Minimum Viable Product**: User Story 1 + User Story 4
- Hero section with satirical Bulgarian branding
- 5 article previews displayed
- Fully responsive mobile experience
- Performance targets met

This delivers core value: visitors see satirical content on any device.

### Parallel Execution Opportunities

**Phase 1 (Setup)**: Tasks T001, T002 can run in parallel (install Hugo + npm)

**Phase 2 (Foundational)**:
- Parallel group 1: T007 (CSS), T008 (baseof.html)
- Parallel group 2: T010 (utilities), T011 (theme CSS files), T015 (header), T016 (footer)

**Phase 3 (US1)**:
- T023 (create articles) can run in parallel with T017-T022 (layout work)

**Phase 8 (Polish)**:
- T073 (fonts), T074 (preload), T075 (placeholder) can all run in parallel

---

## Task Summary

**Total Tasks**: 90

**Tasks by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 11 tasks (BLOCKING)
- Phase 3 (US1 - First-Time Visitor): 10 tasks
- Phase 4 (US4 - Mobile-Optimized): 11 tasks
- Phase 5 (US2 - Article Navigation): 8 tasks
- Phase 6 (US3 - Theme Switching): 12 tasks
- Phase 7 (US5 - SEO & Social): 15 tasks
- Phase 8 (Polish): 13 tasks
- Phase 9 (Documentation): 5 tasks

**Tasks by User Story**:
- US1 (First-Time Visitor Discovery): 10 tasks
- US2 (Article Discovery & Navigation): 8 tasks
- US3 (Theme Switching Experience): 12 tasks
- US4 (Mobile-Optimized Experience): 11 tasks
- US5 (SEO & Social Sharing): 15 tasks
- Infrastructure (Setup + Foundational): 16 tasks
- Shared (Polish + Docs): 18 tasks

**Parallelization Opportunities**: 15+ tasks marked [P]

**Estimated Effort**: 
- MVP (US1 + US4): ~35 tasks, 2-3 days
- Full Feature (All stories): ~90 tasks, 5-7 days

---

## Implementation Strategy

### Week 1: MVP

**Day 1**: Setup + Foundational (T001-T016)
- Install dependencies, configure tools
- Create base templates and theme foundation
- **Checkpoint**: Hugo builds, base layout renders

**Day 2-3**: User Story 1 + 4 (T017-T037)
- Implement hero section and article list
- Create sample articles
- Optimize for mobile and performance
- **Checkpoint**: MVP functional, Lighthouse 90+

### Week 2: Full Feature

**Day 4**: User Story 2 + 3 (T038-T057)
- Add article navigation and interactions
- Implement theme switching
- **Checkpoint**: Interactive features work

**Day 5-6**: User Story 5 + Polish (T058-T085)
- Add SEO metadata and accessibility
- Final optimizations
- Cross-browser testing
- **Checkpoint**: Production ready

**Day 7**: Documentation + Deployment (T086-T090)
- Update docs
- Deploy to production

---

## Testing Approach

Since automated tests are not included, use this manual testing workflow:

### Per User Story Testing

**After each user story phase**:
1. Verify acceptance criteria from spec.md
2. Test independent test scenario
3. Check responsive behavior (320px, 375px, 768px, 1024px+)
4. Validate Bulgarian content present and satirical

### Final Testing (Phase 8)

1. **Lighthouse**: Run audit, verify 90+ scores
2. **Core Web Vitals**: Check LCP, FID, CLS in "Good" range
3. **Accessibility**: Screen reader test, keyboard navigation, contrast check
4. **Cross-browser**: Chrome, Firefox, Safari, Edge
5. **Mobile devices**: Real device testing (iOS + Android)
6. **SEO validators**: Facebook debugger, Google Rich Results Test, W3C HTML validator

### Performance Testing

```bash
# Build for production
hugo --minify

# Serve locally
cd public && python3 -m http.server 8000

# Run Lighthouse in Chrome DevTools (Incognito mode)
# Target scores: All 90+
```

---

## Success Criteria

- [ ] All 5 user stories implemented and tested
- [ ] MVP (US1 + US4) delivers core value independently
- [ ] Lighthouse scores: Performance 90+, Accessibility 90+, Best Practices 90+, SEO 90+
- [ ] Core Web Vitals: LCP <2.5s, FID <100ms, CLS <0.1
- [ ] Page weight: <500KB (excl. images)
- [ ] Mobile responsive: 320px to 4K screens
- [ ] All text in Bulgarian with satirical tone
- [ ] WCAG 2.1 Level AA compliance verified
- [ ] Theme switching works across all 3 modes
- [ ] Open Graph and JSON-LD validated
- [ ] Cross-browser compatible
- [ ] Hugo builds without errors
- [ ] Production deployment successful

---

## Next Steps

1. ✅ Review this task breakdown with team/stakeholders
2. 🚀 Start with Phase 1: Setup (T001-T005)
3. 📋 Move through phases sequentially
4. ✅ Check off tasks as completed
5. 🎯 Validate checkpoints after each phase
6. 🚢 Deploy MVP after completing US1 + US4
7. 🌟 Complete full feature with remaining user stories

**Ready to start implementation!**
