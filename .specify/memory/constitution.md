<!--
SYNC IMPACT REPORT - Constitution Update
=========================================
Version Change: Initial → 1.0.0
Scope: Initial constitution creation for GisheNomerBezkrajnost project

Principles Defined:
  ✅ I. Performance & Mobile-First - Fast loading, optimized for unstable connections
  ✅ II. Bulgarian Content & Satirical Voice - Strict language and tone requirements
  ✅ III. Hugo Best Practices (NON-NEGOTIABLE) - Modern Hugo features, minimal reinvention
  ✅ IV. Minimal External Dependencies - Self-contained, maintainable codebase
  ✅ V. Accessibility & SEO Excellence - WCAG compliance, search optimization
  ✅ VI. Modern Design System - TailwindCSS, Apple-style, theme support
  ✅ VII. Monetization Readiness - Ad-friendly, social media optimized

Templates Requiring Updates:
  ⚠ plan-template.md - Constitution Check gates need Hugo-specific validation
  ⚠ spec-template.md - User stories should align with content/article focus
  ⚠ tasks-template.md - Task categories should reflect Hugo theme development

Follow-up TODOs:
  - Update plan-template.md Constitution Check to validate Hugo structure
  - Ensure spec-template.md examples reflect article/content creation workflows
  - Add Hugo-specific task categories to tasks-template.md (theme, shortcodes, archetypes)

Suggested commit message:
docs: create constitution v1.0.0 for Bulgarian satirical website project
-->

# GisheNomerBezkrajnost (Гише безкрайност) Constitution

## Core Principles

### I. Performance & Mobile-First

**MUST**: All pages render in under 2 seconds on 3G connections; Images MUST be optimized and lazy-loaded; CSS and JavaScript MUST be minified and inlined where appropriate; Core Web Vitals MUST meet "Good" thresholds (LCP <2.5s, FID <100ms, CLS <0.1); Desktop AND mobile experiences MUST be equally optimized.

**MUST NOT**: Introduce dependencies that bloat bundle size; Use unoptimized images or heavy external resources; Sacrifice mobile experience for desktop features.

**Rationale**: Target audience may have unstable internet. Fast loading is critical for engagement and monetization through ads. Performance directly impacts SEO rankings and user retention.

### II. Bulgarian Content & Satirical Voice

**MUST**: All content MUST be written in Bulgarian language (bg-BG); Tone MUST be satirical, funny, and absurd; Articles MUST focus on bureaucracy and culture of Bulgarian institutions; Content MUST maintain consistency in satirical voice across all pages.

**MUST NOT**: Include content in other languages (except metadata for SEO); Use serious or formal tone; Deviate from the satirical theme about Bulgarian bureaucracy.

**Rationale**: The project's unique value proposition is Bulgarian-language satirical content. Language and tone consistency are essential for brand identity and audience engagement.

### III. Hugo Best Practices (NON-NEGOTIABLE)

**MUST**: Use Hugo's built-in features (partials, shortcodes, archetypes, taxonomies) instead of custom implementations; Leverage Hugo's asset pipeline for CSS/JS processing; Use Hugo's image processing for optimization; Follow Hugo's content organization conventions; Keep hugo.toml configuration clean and well-documented.

**MUST NOT**: Reinvent functionality already provided by Hugo; Create custom build scripts when Hugo has native support; Ignore Hugo's recommended project structure.

**Rationale**: Hugo is chosen for its speed and simplicity. Using modern Hugo features ensures maintainability, community support, and future-proofing. Custom solutions increase technical debt.

### IV. Minimal External Dependencies

**MUST**: Prefer vanilla JavaScript over frameworks; Keep npm/package.json dependencies to absolute minimum; Use TailwindCSS via Hugo's asset pipeline without external build tools where possible; Self-host critical assets (fonts, icons).

**MUST NOT**: Add JavaScript libraries for functionality achievable with vanilla JS; Include unused CSS frameworks or UI component libraries; Depend on external CDNs for critical rendering resources.

**Rationale**: External dependencies increase load time, create security vulnerabilities, and complicate maintenance. Minimal dependencies ensure long-term sustainability.

### V. Accessibility & SEO Excellence

**MUST**: Follow WCAG 2.1 Level AA guidelines; Provide semantic HTML5 structure; Include ARIA labels where appropriate; Implement Open Graph and Twitter Card metadata; Generate valid XML sitemaps; Use structured data (JSON-LD) for articles; Ensure keyboard navigation works throughout.

**MUST NOT**: Use color alone to convey information; Create keyboard traps; Omit alt text for images; Ignore meta descriptions or page titles.

**Rationale**: Accessibility is a legal and ethical requirement. SEO optimization is critical for organic growth and monetization potential. Both drive traffic and engagement.

### VI. Modern Design System

**MUST**: Use TailwindCSS for styling with modern, clean aesthetics; Implement Apple-style design patterns (minimal, spacious, typography-focused); Use modern web fonts optimized for Bulgarian Cyrillic; Support three theme modes: light, dark, and system (default to system); Ensure theme switching is instant without page reload; Maintain consistent spacing, typography, and color schemes across themes.

**MUST NOT**: Use outdated CSS patterns or table-based layouts; Implement themes that look inconsistent or poorly designed; Use fonts that don't support Cyrillic characters properly.

**Rationale**: Modern, attractive design differentiates the site from old-fashioned Bulgarian websites. Apple-style aesthetics convey professionalism and quality. Theme support improves user experience and accessibility.

### VII. Monetization Readiness

**MUST**: Design layouts with ad placement zones (header, sidebar, in-content); Ensure ad spaces don't negatively impact Core Web Vitals; Create shareable content optimized for social media (Open Graph images, Twitter cards); Track user engagement with privacy-respecting analytics; Design for viral sharing through social channels.

**MUST NOT**: Compromise user experience with intrusive ads; Violate GDPR/privacy regulations; Make the site unusable on ad blockers.

**Rationale**: Monetization through ads and social media is the ultimate goal. The technical foundation must support these revenue streams while maintaining quality user experience.

## Technical Standards

### Hugo & Theme Structure

- **Hugo Version**: Use latest stable Hugo Extended (required for SCSS/TailwindCSS processing)
- **Theme**: Custom theme "sarcastic" in `themes/sarcastic/`
- **Content Type**: Primary content type is "article" (archetypes/article.md)
- **Asset Pipeline**: Use Hugo Pipes for CSS/JS bundling, minification, and fingerprinting
- **Image Processing**: Use Hugo's image processing functions for responsive images
- **Templating**: Use Go templates following Hugo conventions (baseof.html, partials, blocks)

### Styling & Frontend

- **CSS Framework**: TailwindCSS configured via Hugo asset pipeline
- **JavaScript**: Vanilla ES6+ only; no frameworks unless justified
- **Fonts**: Self-hosted modern web fonts with full Cyrillic support
- **Icons**: SVG icons inlined or sprite-based for performance
- **Theme Implementation**: CSS variables for theme colors; localStorage for preference persistence; Respect prefers-color-scheme media query

### Content & SEO

- **Language Code**: bg-BG throughout
- **URL Structure**: Clean, descriptive URLs in Bulgarian (transliterated if needed)
- **Metadata**: Complete frontmatter for all articles (title, description, date, tags, categories)
- **Structured Data**: JSON-LD for Article schema on all posts
- **Social Sharing**: Open Graph and Twitter Card meta tags on all pages

### Performance Targets

- **Lighthouse Score**: 90+ for all categories (Performance, Accessibility, Best Practices, SEO)
- **Core Web Vitals**: LCP <2.5s, FID <100ms, CLS <0.1
- **Page Weight**: <500KB for article pages (without images), <1MB total
- **Build Time**: Full site build <10 seconds for <100 articles

## Development Workflow

### Content Creation

1. Use Hugo archetypes for consistent article structure
2. Write content in Bulgarian with satirical tone
3. Optimize images before adding to content (WebP format preferred)
4. Test article rendering in all three themes
5. Validate metadata and social sharing previews

### Theme Development

1. Changes to theme MUST be tested across all theme modes (light/dark/system)
2. New components MUST follow TailwindCSS utility-first patterns
3. JavaScript features MUST degrade gracefully without JS enabled
4. Layout changes MUST be tested on mobile and desktop
5. Performance impact MUST be measured before merging

### Quality Gates

- All pages MUST validate as HTML5
- No console errors in production build
- Lighthouse scores MUST meet targets
- Theme switching MUST work without flicker
- Content MUST be readable in all themes
- Mobile navigation MUST be fully functional

## Governance

This constitution supersedes all other development practices and decisions. All changes, features, and content MUST comply with these principles.

**Amendment Process**: Amendments require clear justification, impact analysis on existing features, and approval before implementation. Version bumps follow semantic versioning:

- **MAJOR**: Breaking changes to core principles or architecture
- **MINOR**: New principles added or significant expansions
- **PATCH**: Clarifications, wording improvements, non-semantic changes

**Compliance**: All pull requests, code reviews, and feature implementations MUST verify compliance with this constitution. Any deviation MUST be explicitly justified with technical rationale and approved.

**Enforcement**: Constitution violations block merging. Performance regressions require rollback or immediate fix. Theme or accessibility issues are high-priority bugs.

**Version**: 1.0.0 | **Ratified**: 2025-10-12 | **Last Amended**: 2025-10-12
