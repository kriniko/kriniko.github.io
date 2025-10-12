# Гише безкрайност (Гише8)

Сатиричен портал за безкрайната бюрокрация в България. Забавни истории, абсурдни правила и документи без край.

## Технологии

- **Hugo Extended** v0.151+ - Статичен генератор на сайтове
- **TailwindCSS** v4.1 - CSS framework
- **Vanilla JavaScript** ES6+ - Тема switcher
- **Inter Font** - Модерен шрифт с пълна поддръжка на кирилица

## Локална разработка

### Предварителни изисквания

- Hugo Extended (v0.151+)
- Node.js (18+)
- npm (10+)

### Инсталация

```bash
# Клониране на хранилището
git clone https://github.com/kriniko/GisheNomerBezkrajnost.git
cd GisheNomerBezkrajnost

# Инсталиране на зависимости
npm install

# Стартиране на dev сървър
hugo server
```

Сайтът ще бъде достъпен на `http://localhost:1313`

### Билд за продукция

```bash
# Генериране на оптимизиран билд
hugo --minify

# Изходът е в директория public/
```

## Deployment (GitHub Pages)

Сайтът автоматично се публикува на GitHub Pages при всеки push към `main` или `001-home-page` branch.

### Настройка (еднократна)

1. Отидете на Settings → Pages в GitHub репозиторито
2. Под "Build and deployment" изберете:
   - **Source**: Deploy from a branch
   - **Branch**: gh-pages (ще бъде създаден автоматично)
3. Уверете се, че в Settings → Actions → General:
   - **Workflow permissions**: Read and write permissions е избрано

### Как работи

Workflow-ът използва [Hugo Deploy GitHub Pages](https://github.com/marketplace/actions/hugo-deploy-github-pages) action, който:
- Билдва сайта с Hugo Extended v0.151.0
- Push-ва резултата към `gh-pages` branch
- GitHub Pages сервира сайта от този branch

### Ръчно задействане

```bash
# Push промени към GitHub
git push origin 001-home-page

# Или ръчно от GitHub Actions таб
# Actions → Deploy Hugo site → Run workflow
```

Сайтът ще бъде достъпен на: `https://kriniko.github.io/GisheNomerBezkrajnost/`

### Custom Domain (опционално)

За да използвате собствен домейн:

1. Добавете домейна в `.github/workflows/deploy-hugo.yml`:
   ```yaml
   CNAME: 'gishe8.com'
   ```

2. Конфигурирайте DNS записите при вашия доставчик:
   - CNAME запис: `gishe8.com` → `kriniko.github.io`

3. В GitHub Settings → Pages добавете custom domain и активирайте HTTPS

## Структура на проекта

```
.
├── content/           # Съдържание на сайта
│   ├── _index.md     # Начална страница
│   └── article/      # Статии
├── themes/sarcastic/ # Тема
│   ├── assets/       # CSS, JS файлове
│   └── layouts/      # HTML шаблони
├── static/           # Статични файлове
└── hugo.toml         # Конфигурация
```

## Добавяне на нова статия

```bash
# Създаване на нова статия
hugo new content/article/заглавие-на-статията.md
```

Или ръчно създайте файл в `content/article/` със следната структура:

```markdown
---
title: "Заглавие на статията"
date: 2025-10-12
description: "Кратко описание"
draft: false
---

Съдържание на статията...
```

## Функционалности

- ✅ Адаптивен дизайн (mobile-first)
- ✅ Светла/тъмна/системна тема
- ✅ SEO оптимизация
- ✅ Социални метаданни (Open Graph, Twitter Cards)
- ✅ Структурирани данни (JSON-LD)
- ✅ Достъпност (WCAG 2.1 AA)
- ✅ Производителност (Core Web Vitals)

## Производителност

- Lighthouse Score: 90+
- Page Weight: <500KB (без изображения)
- Load Time: <2s на 3G
