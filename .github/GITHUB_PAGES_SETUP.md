# GitHub Pages Deployment Setup

This document explains how to deploy the Hugo site to GitHub Pages using the [Hugo Deploy GitHub Pages](https://github.com/marketplace/actions/hugo-deploy-github-pages) action.

## Overview

The site uses a GitHub Actions workflow (`.github/workflows/deploy-hugo.yml`) to automatically build and deploy the Hugo site to GitHub Pages whenever code is pushed to the `main` or `001-home-page` branch.

This workflow uses the **benmatselby/hugo-deploy-gh-pages** action which:
- Builds your Hugo site with the specified version and arguments
- Pushes the built site to a `gh-pages` branch
- GitHub Pages serves the site from that branch

## One-Time Setup

### 1. Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/kriniko/GisheNomerBezkrajnost`
2. Click on **Settings** → **Pages** (in the left sidebar)
3. Under **Build and deployment**:
   - **Source**: Select **Deploy from a branch**
   - **Branch**: Select **gh-pages** (will be created automatically by the workflow)
   - **Folder**: Select **/ (root)**
4. Click **Save**

### 2. Verify Workflow Permissions

The workflow uses `GITHUB_TOKEN` which is automatically provided by GitHub Actions.

1. Go to **Settings** → **Actions** → **General**
2. Scroll down to **Workflow permissions**
3. Ensure **Read and write permissions** is selected
4. Click **Save**

### 3. Update Configuration (if needed)

If you want to use a custom domain, update the workflow file `.github/workflows/deploy-hugo.yml`:

```yaml
env:
  CNAME: 'gishe8.com'  # Add your custom domain here
```

## How It Works

### Workflow Triggers

The workflow runs automatically on:
- **Push** to `main` branches
- **Manual trigger** from the Actions tab

### Build Process

1. **Install Hugo Extended** (v0.151.0)
2. **Install Dart Sass** for styling
3. **Checkout repository** with submodules
4. **Setup Node.js** (v20) and install npm dependencies
5. **Build Hugo site** with:
   - Garbage collection (`--gc`)
   - Minification (`--minify`)
   - Production environment variables
6. **Upload artifact** to GitHub Pages

### Deployment

- Deploys the built site from the `public/` directory
- Uses GitHub's official `deploy-pages` action
- Site URL: `https://kriniko.github.io/GisheNomerBezkrajnost/`

## Manual Deployment

You can manually trigger a deployment:

1. Go to **Actions** tab in your GitHub repository
2. Select **Deploy Hugo site to GitHub Pages**
3. Click **Run workflow**
4. Select the branch (usually `main` or `001-home-page`)
5. Click **Run workflow**

## Troubleshooting

### Build Fails

**Check the Actions logs:**
1. Go to **Actions** tab
2. Click on the failed workflow run
3. Expand the failed step to see error messages

**Common issues:**
- Missing npm dependencies: Run `npm install` locally and commit `package-lock.json`
- Hugo version mismatch: Ensure `HUGO_VERSION` in workflow matches your local version
- TailwindCSS errors: Check `postcss.config.js` and `main.css` syntax

### Site Not Updating

1. Verify GitHub Pages is enabled (Settings → Pages → Source: GitHub Actions)
2. Check that the workflow completed successfully (green checkmark in Actions tab)
3. Clear browser cache or open in incognito mode
4. GitHub Pages can take 1-2 minutes to update after deployment

### 404 Errors

If you see 404 errors on the deployed site:

1. Check `hugo.toml` baseURL matches your GitHub Pages URL:
   ```toml
   baseURL = 'https://kriniko.github.io/GisheNomerBezkrajnost/'
   ```

2. Or use relative URLs:
   ```toml
   relativeURLs = true
   ```

## Environment Variables

The workflow uses these environment variables during build:

- `HUGO_ENVIRONMENT=production` - Enables production optimizations
- `HUGO_CACHEDIR` - Caches Hugo build artifacts
- `TZ=Europe/Sofia` - Sets timezone for dates

## Customization

### Change Deployment Branch

Edit `.github/workflows/deploy-hugo.yml`:

```yaml
on:
  push:
    branches:
      - main           # Change this to your desired branch
      - other-branch
```

### Change Hugo Version

Update the `HUGO_VERSION` in the workflow:

```yaml
env:
  HUGO_VERSION: 0.151.0  # Change to desired version
```

### Add Custom Domain

1. Add a `CNAME` file to the `static/` directory:
   ```
   gishe8.com
   ```

2. Configure DNS with your domain provider:
   - Add CNAME record pointing to `kriniko.github.io`

3. In GitHub Settings → Pages:
   - Enter your custom domain
   - Enable **Enforce HTTPS**

## Monitoring

### Build Status Badge

Add this to your README.md to show build status:

```markdown
![Deploy Hugo](https://github.com/kriniko/GisheNomerBezkrajnost/actions/workflows/deploy-hugo.yml/badge.svg)
```

### Deployment History

View all deployments:
- Go to **Actions** tab
- Filter by workflow: **Deploy Hugo site to GitHub Pages**
- See successful/failed runs with timestamps

## Security

The workflow uses:
- **Minimal permissions** (contents: read, pages: write)
- **Official GitHub Actions** (no third-party actions for deployment)
- **Dependabot** compatible (will auto-update action versions)

## Performance

The deployed site includes:
- **Minified CSS/JS** (via `--minify` flag)
- **Optimized images** (via Hugo image processing)
- **CDN delivery** (GitHub Pages global CDN)
- **HTTPS** (automatic via GitHub Pages)

## Costs

GitHub Pages is **free** for public repositories with:
- 1GB storage limit
- 100GB bandwidth per month
- 10 builds per hour

For private repositories, you need GitHub Pro/Team/Enterprise.
