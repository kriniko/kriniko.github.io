# Data Model: Home Page

**Feature**: Home Page  
**Branch**: 001-home-page  
**Date**: 2025-10-12  
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data structures and content models for the GisheNomerBezkrajnost home page. Since this is a Hugo static site, "entities" are represented as content types (archetypes), frontmatter fields, and configuration parameters rather than database schemas.

## Content Types

### 1. Home Page (Content Type: `_index.md`)

**File Location**: `content/_index.md`

**Purpose**: Root page content and metadata for the home page.

**Frontmatter Fields**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `title` | string | Yes | Site title | "Гише безкрайност" |
| `description` | string | Yes | Meta description for SEO | "Добре дошли в безкрайността на българската бюрокрация" |
| `tagline` | string | Yes | Hero section tagline | "Пътуването през безбройните гишета на администрацията" |
| `keywords` | array | No | SEO keywords | ["бюрокрация", "гишета", "сатира"] |
| `image` | string | No | Social sharing image | "/images/og-image.jpg" |
| `type` | string | No | Content type | "home" (for layout selection) |

**Content Body**: Optional markdown content for additional hero section text.

**Example**:
```yaml
---
title: "Гише безкрайност"
description: "Сатиричен портал за безкрайната бюрокрация в България"
tagline: "Добре дошли в безкрайността на българската бюрокрация"
keywords:
  - бюрокрация
  - гишета
  - сатира
  - България
  - администрация
image: "/images/og-home.jpg"
type: "home"
---

Тук започва пътуването ви през лабиринта от гишета, формуляри и абсурдни правила.
```

---

### 2. Article (Content Type: `article`)

**File Location**: `content/article/[article-slug].md`

**Purpose**: Individual satirical articles about Bulgarian bureaucracy.

**Frontmatter Fields**:

| Field | Type | Required | Description | Example | Validation |
|-------|------|----------|-------------|---------|------------|
| `title` | string | Yes | Article title | "Как да подадете молба за неподаване на молби" | Max 80 chars (truncate with ellipsis) |
| `date` | datetime | Yes | Publication date | "2025-10-12T14:30:00+02:00" | ISO 8601 format |
| `draft` | boolean | No | Draft status | false | Default: true |
| `description` | string | Yes | Article summary for previews | "Новата процедура изисква 7 печата и 3 непублични празника" | 100-150 chars |
| `author` | string | No | Author name | "Редакция" | Optional |
| `tags` | array | No | Article tags | ["форми", "молби", "абсурд"] | Max 5 tags |
| `categories` | array | No | Article categories | ["Процедури"] | Max 3 categories |
| `featured_image` | string | No | Article featured image | "featured.jpg" | Relative to article folder |
| `image_alt` | string | Conditional | Alt text for image | "Човек чака на гише с 50 документа" | Required if featured_image exists |
| `weight` | int | No | Sort order (lower = higher priority) | 10 | For manual ordering |

**Content Body**: Main article content in markdown, Bulgarian language, satirical tone.

**Example**:
```yaml
---
title: "Електронната услуга изисква 3 посещения на гише"
date: 2025-10-12T10:00:00+02:00
draft: false
description: "Новата е-услуга обещава да спести време, но първо трябва да посетите Гише 8, 12 и 15 за активация"
tags:
  - е-услуги
  - гишета
  - модернизация
categories:
  - Електронно управление
featured_image: "e-usluga.jpg"
image_alt: "Компютър на гише с надпис 'Извън експлоатация от 2015'"
---

## Революцията в администрацията

Днес беше обявена нова електронна услуга...
```

---

### 3. Site Configuration (Config Type: `hugo.toml`)

**File Location**: `hugo.toml` (repository root)

**Purpose**: Global site configuration and theme parameters.

**Key Configuration Sections**:

**Basic Settings**:
```toml
baseURL = 'https://gishe8.com/'
languageCode = 'bg-BG'
title = 'Гише безкрайност'
theme = 'sarcastic'
defaultContentLanguage = 'bg'
```

**Site Parameters**:
```toml
[params]
  description = "Сатиричен портал за българската бюрокрация"
  author = "Редакция Гише8"
  
  # SEO
  keywords = ["бюрокрация", "сатира", "България", "гишета"]
  
  # Social
  twitter = "@gishe8"  # If exists
  facebook = "gishe8"  # If exists
  
  # Theme
  defaultTheme = "system"  # light, dark, or system
  
  # Performance
  imageProcessing = true
  lazyLoadImages = true
  
  # Monetization (future)
  enableAds = false
  
  # Article preview settings
  homeArticleCount = 5  # Number of articles on home page
  excerptLength = 150   # Characters for summaries
```

**Menu Configuration**:
```toml
[[menu.main]]
  name = "Начало"
  url = "/"
  weight = 1

[[menu.main]]
  name = "Статии"
  url = "/article/"
  weight = 2

[[menu.main]]
  name = "За нас"
  url = "/about/"
  weight = 3
```

---

### 4. Theme Preference (Client-Side Storage)

**Storage Location**: `localStorage` (browser)

**Purpose**: Persist user's theme choice across sessions.

**Data Structure**:

| Key | Value Type | Possible Values | Description |
|-----|------------|-----------------|-------------|
| `gishe-theme` | string | "light", "dark", "system" | User's theme preference |

**Storage Logic**:
- Read on page load to apply theme immediately
- Write when user changes theme via switcher
- Default to "system" if not set
- Fallback to "light" if localStorage unavailable

**JavaScript Interface**:
```javascript
// Get theme
const theme = localStorage.getItem('gishe-theme') || 'system';

// Set theme
localStorage.setItem('gishe-theme', 'dark');

// Clear theme (reset to default)
localStorage.removeItem('gishe-theme');
```

---

## Data Relationships

### Home Page → Articles

**Relationship Type**: One-to-Many (Home page displays multiple articles)

**Query Logic** (Hugo template):
```go-html-template
{{- $articles := where site.RegularPages "Type" "article" -}}
{{- $articles = where $articles "Draft" false -}}
{{- $articles = $articles | first 5 -}}
{{- range $articles -}}
  <!-- Display article card -->
{{- end -}}
```

**Sorting**: By date (newest first)

**Filtering**: 
- Only published articles (draft: false)
- Only "article" content type
- Limit to 5 most recent

---

### Article → Tags/Categories

**Relationship Type**: Many-to-Many (Articles can have multiple tags/categories)

**Hugo Taxonomy**: Built-in tags and categories taxonomies

**Query Examples**:
```go-html-template
<!-- Get article tags -->
{{ range .Params.tags }}
  <span class="tag">{{ . }}</span>
{{ end }}

<!-- Get all articles in category -->
{{ range (where .Site.Pages "Params.categories" "intersect" (slice "Процедури")) }}
  <!-- Article list -->
{{ end }}
```

---

## Validation Rules

### Article Title
- **Rule**: Maximum 80 characters
- **Action**: Truncate with ellipsis (...) for display
- **Reason**: Prevent layout breaking on mobile, maintain design consistency

### Article Description
- **Rule**: 100-150 characters recommended
- **Action**: Warn if outside range, truncate at 160 for meta description
- **Reason**: Optimal length for article previews and SEO snippets

### Featured Image
- **Rule**: If `featured_image` specified, `image_alt` is required
- **Action**: Build error or warning if missing
- **Reason**: Accessibility requirement (WCAG 2.1 Level AA)

### Publication Date
- **Rule**: Must be valid ISO 8601 datetime
- **Action**: Hugo build error if invalid
- **Reason**: Required for sorting and SEO

### Language
- **Rule**: All content must be in Bulgarian (bg-BG)
- **Action**: Editorial review (no automated check)
- **Reason**: Constitutional requirement (Principle II)

### Draft Status
- **Rule**: Default to `draft: true` for new articles
- **Action**: Must explicitly set to `false` to publish
- **Reason**: Prevent accidental publication of unfinished content

---

## State Transitions

### Article Lifecycle

```
┌─────────┐
│  Draft  │ (draft: true, not visible on site)
└────┬────┘
     │ Author sets draft: false
     ↓
┌─────────┐
│Published│ (draft: false, visible on home page & article list)
└────┬────┘
     │ Author sets draft: true (or removes file)
     ↓
┌─────────┐
│Unpublish│ (removed from public view, still in repo)
└─────────┘
```

### Theme Preference Lifecycle

```
┌──────────┐
│  System  │ (Default: follows OS preference)
└────┬─────┘
     │ User clicks Light/Dark theme button
     ├─────────────────┬─────────────────┐
     ↓                 ↓                 ↓
┌────────┐       ┌─────────┐      ┌────────┐
│ Light  │       │  Dark   │      │ System │
└────────┘       └─────────┘      └────────┘
     │                 │                 │
     └─────────────────┴─────────────────┘
              User can switch at any time
              (Preference saved in localStorage)
```

---

## Content Examples

### Minimal Article
```yaml
---
title: "Гише 8 работи само в сряда"
date: 2025-10-12T15:00:00+02:00
draft: false
description: "Но само в сряди, които са втори вторник на месеца"
---

Администрацията съобщава...
```

### Full Article with All Fields
```yaml
---
title: "Пълното ръководство за попълване на Формуляр 42-Б"
date: 2025-10-12T09:00:00+02:00
draft: false
description: "Формулярът изисква формуляр 42-А, който съществува само в теорията"
author: "Старши експерт по формуляри"
tags:
  - формуляри
  - процедури
  - абсурд
  - 42-Б
categories:
  - Документи
  - Процедури
featured_image: "formular-42b.jpg"
image_alt: "Стълб от документи до тавана с надпис 'Приложение 1 от 847'"
weight: 5
---

## Въведение

Формуляр 42-Б е централен елемент...
```

---

## Hugo Archetypes

### Article Archetype Template

**File**: `archetypes/article.md`

```markdown
---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
description: ""
tags: []
categories: []
featured_image: ""
image_alt: ""
---

## Въведение

[Напишете въведение тук...]

## Основна част

[Развийте темата...]

## Заключение

[Финални мисли...]
```

**Usage**:
```bash
hugo new article/nov-absurd-na-gishe-8.md
```

---

## Performance Considerations

### Image Processing

**Hugo Image Processing** (in templates):
```go-html-template
{{- with .Resources.GetMatch "featured-image.*" -}}
  {{- $small := .Resize "400x webp q85" -}}
  {{- $medium := .Resize "800x webp q85" -}}
  {{- $large := .Resize "1200x webp q85" -}}
  
  <img src="{{ $medium.RelPermalink }}"
       srcset="{{ $small.RelPermalink }} 400w,
               {{ $medium.RelPermalink }} 800w,
               {{ $large.RelPermalink }} 1200w"
       sizes="(max-width: 600px) 400px,
              (max-width: 1200px) 800px,
              1200px"
       loading="lazy"
       alt="{{ $.Params.image_alt }}"
       width="{{ $medium.Width }}"
       height="{{ $medium.Height }}">
{{- end -}}
```

**Result**: Responsive images, WebP format, lazy loading, proper dimensions to prevent CLS.

---

## Summary

**Content Types Defined**: 3
- Home Page (`_index.md`)
- Article (`article/*.md`)
- Site Configuration (`hugo.toml`)

**Client-Side Storage**: 1
- Theme Preference (localStorage)

**Total Fields**: 25+ across all content types

**Validation Rules**: 6 enforced rules

**State Transitions**: 2 lifecycles (Article, Theme)

All entities align with Hugo best practices and constitutional requirements (Performance, Accessibility, SEO, Bulgarian Content).
