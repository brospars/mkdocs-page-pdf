# MkDocs Page to PDF

[![PyPI version](https://img.shields.io/pypi/v/mkdocs-page-pdf)](https://pypi.org/project/mkdocs-page-pdf/)
[![Python versions](https://img.shields.io/pypi/pyversions/mkdocs-page-pdf)](https://pypi.org/project/mkdocs-page-pdf/)
[![Downloads](https://img.shields.io/pypi/dm/mkdocs-page-pdf)](https://pypi.org/project/mkdocs-page-pdf/)
[![License: MIT](https://img.shields.io/pypi/l/mkdocs-page-pdf)](https://github.com/brospars/mkdocs-page-pdf/blob/master/LICENSE)

**Export your MkDocs documentation to PDF**: one PDF per page with a download button, and/or a single PDF of the whole site with a cover page, bookmarks and continuous page numbers.

PDFs are rendered with headless Chromium ([Playwright](https://playwright.dev/python/)), so they look exactly like your site in the browser: same theme, CSS, images, code highlighting and math. Works with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and multi-language sites ([mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n)).


## Features

- **One PDF per page**, with a download button added to each page (Material for MkDocs).
- **Combined PDF** of the whole site, in navigation order, with:
  - a customizable **cover page**,
  - a **bookmark** (PDF outline) for each page,
  - **continuous page numbers** in headers and footers.
- **Combined only** mode: just one PDF for the whole documentation.
- **Custom headers and footers** using Jinja (`{{ page.title }}`, `{{ config.site_name }}`...), inline or from external `.html` files.
- **Fast builds**: pages are rendered in parallel with bounded memory usage, configurable for CI runners.
- Fine control over the output: paper format, margins, landscape, scale, background graphics, page ranges, excluded pages.


## Quick Start

### 1. Install the plugin and Chromium

```shell
pip install mkdocs-page-pdf
playwright install chromium
```

### 2. Enable the plugin in `mkdocs.yml`

```yaml
plugins:
  - search
  - page-to-pdf  # Should be last to ensure all content is rendered
```

Run `mkdocs build`: each page now has a PDF next to its HTML file and a download button.


## Usage Examples

### One PDF per page (default)

```yaml
plugins:
  - page-to-pdf:
      format: A4
      printBackground: true
      exclude:
        - "index.md"
        - "blog/*"
```

### A single PDF for the whole site

Generate one PDF of the documentation, with a cover page, bookmarks and page numbers, in addition to the per-page PDFs:

```yaml
plugins:
  - page-to-pdf:
      combined: true
      combinedFilename: pdf/documentation.pdf
      displayHeaderFooter: true
      footerTemplate: '<div style="font-size: 9px; width: 100%; text-align: center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
```

Link to it from your docs or your navigation, e.g. `[Download the documentation (PDF)](pdf/documentation.pdf)`.

To generate **only** the combined PDF (no per-page PDFs or download buttons), use `combinedOnly: true` instead of `combined: true`.

### Custom headers, footers and cover page from files

```yaml
plugins:
  - page-to-pdf:
      combined: true
      displayHeaderFooter: true
      headerTemplate: templates/pdf-header.html
      footerTemplate: templates/pdf-footer.html
      coverTemplate: templates/pdf-cover.html
```

Paths are relative to `mkdocs.yml`. Example `templates/pdf-header.html`:

```html
<div style="font-size: 9px; width: 100%; padding: 0 20px; display: flex; justify-content: space-between">
  <span>{{ config.site_name }}</span>
  <span>{{ page.title }}</span>
</div>
```


## Options

All options are set under the plugin in `mkdocs.yml`:

```yaml
plugins:
  - page-to-pdf:
      # Options here
```

### General

| Option | Type | Default | Description |
|---|---|---|---|
| `disable` | bool | `false` | Disable PDF rendering, without removing the plugin configuration. |
| `disableOnServe` | bool | `false` | Disable PDF rendering when using `mkdocs serve`. |
| `concurrency` | int | `min(4, CPUs)` | Maximum number of pages rendered at the same time. Higher values speed up the build but use more memory (each page is a Chromium tab). Use `1` for sequential rendering. |
| `exclude` | list | `[]` | Glob patterns of source files (e.g. `blog/*`, `index.md`) for which no PDF is generated at all. |

### PDF rendering

Based on [Playwright's `page.pdf()`](https://playwright.dev/python/docs/api/class-page#page-pdf).

| Option | Type | Default | Description |
|---|---|---|---|
| `format` | str | `"A4"` | Paper format (`A4`, `Letter`, `Legal`, `A3`...). |
| `landscape` | bool | `false` | Use landscape orientation. |
| `margin` | dict | `20px` on each side | Paper margins: `top`, `right`, `bottom`, `left`. |
| `scale` | float | `1.0` | Scale of the webpage rendering. |
| `printBackground` | bool | `false` | Print background colors and images. |
| `pageRanges` | str | `""` | Page ranges to print, e.g. `'1-5, 8, 11-13'`. Empty means all pages. |
| `displayHeaderFooter` | bool | `false` | Display the header and footer templates. |
| `headerTemplate` | str | `""` | HTML template for the print header, inline or path to an `.html` file. See [Headers and footers](#headers-and-footers). |
| `footerTemplate` | str | `""` | HTML template for the print footer, inline or path to an `.html` file. |
| `pageLoadOptions` | dict | `{timeout: 30000, waitUntil: "load"}` | Page load options (see [Playwright's `page.goto()`](https://playwright.dev/python/docs/api/class-page#page-goto)). Use `waitUntil: networkidle` if your pages load content asynchronously (e.g. MathJax from a CDN). |

### Per-page download button

| Option | Type | Default | Description |
|---|---|---|---|
| `downloadLink` | str | PDF icon (SVG) | HTML of the download button added to each page. Rendered with Jinja using the page context. The button is inserted in pages built with Material for MkDocs. |

### Combined PDF

| Option | Type | Default | Description |
|---|---|---|---|
| `combined` | bool | `false` | Also generate a single PDF of all pages, in navigation order, with a bookmark for each page. Only pages listed in the `nav` are included. |
| `combinedOnly` | bool | `false` | Generate only the combined PDF: no per-page PDFs and no download buttons. Implies `combined: true`. |
| `combinedFilename` | str | `"combined.pdf"` | Path of the combined PDF, relative to the site root. With a multi-language site, one combined PDF is generated per language, next to each language's homepage (e.g. `combined.pdf` and `en/combined.pdf`). |
| `combinedExclude` | list | `[]` | Glob patterns of pages to leave out of the combined PDF only. Unlike `exclude`, these pages still get their own PDF and download button. |
| `coverTemplate` | str | simple cover | HTML of the cover page, inline or path to an `.html` file. The default shows the theme logo (`theme.logo`, if set) and the site name. Set to `""` to disable the cover page. |

### Headers and footers

`headerTemplate` and `footerTemplate` accept the following classes, filled in by Chromium:

- `date`: formatted print date
- `title`: document title
- `url`: document location
- `pageNumber`: current page number
- `totalPages`: total number of pages

They are also rendered with Jinja using the page context, so you can use `{{ page.title }}`, `{{ page.meta }}`, `{{ config.site_name }}`, etc.

**Note:** Chromium uses a very small default font size in headers and footers: set a `font-size` in your template.

In the combined PDF, each page keeps its own header and footer, and `pageNumber` / `totalPages` are numbered continuously across the whole document (the cover page is not counted).

### Cover page

The cover page is rendered with Jinja using `config` (the MkDocs configuration) and `nav`. Relative links (images, CSS) resolve from the site root. The default cover page is:

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: sans-serif; text-align: center; padding-top: 25vh">
  {% if config.theme.logo %}<img src="{{ config.theme.logo }}" width="120">{% endif %}
  <h1>{{ config.site_name }}</h1>
</body>
</html>
```


## Troubleshooting

### Running in a Docker Container (CI/CD)
If you encounter issues running Playwright in Docker (e.g., `Browser closed unexpectedly`), you may need to install additional system dependencies for Chromium:

```shell
playwright install --with-deps chromium
```

#### Recommended Docker Image
Use a ready-to-use Docker image with all dependencies pre-installed:
- [brospars/docker-mkdocs](https://github.com/brospars/docker-mkdocs)

#### Manual Setup
If you prefer to set up your own image, refer to:
- [Playwright Docker Guide](https://playwright.dev/docs/docker)
- [Puppeteer Troubleshooting in Docker](https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md#running-puppeteer-in-docker)

### Out of Memory in CI
If the build crashes or gets killed on a CI runner with limited memory, lower the `concurrency` option. You can use MkDocs' `!ENV` tag to set it only in CI:

```yaml
plugins:
  - page-to-pdf:
      concurrency: !ENV [PDF_CONCURRENCY, 4]
```

Then set `PDF_CONCURRENCY=1` (or `2`) in your CI environment.

### Slow Build on Serve
To speed up `mkdocs serve`, use the `--dirtyreload` flag to rebuild only modified files:

```shell
mkdocs serve --dirtyreload
```

Alternatively, use the `disableOnServe` option to disable PDF generation during development.

### Blank Page at the End
Due to a Chromium bug, a blank page may appear at the end of the PDF. To fix this, add the following CSS to your `extra.css`:

```css
body {
    contain: strict;
}
```

### Missing Math Formulas or Dynamic Content
If some content is rendered by JavaScript after the page has loaded (MathJax, diagrams...), it may be missing from the PDF. Wait for the network to be idle before rendering:

```yaml
plugins:
  - page-to-pdf:
      pageLoadOptions:
        waitUntil: networkidle
        timeout: 30000
```


## Changelog

See [CHANGELOG.md](https://github.com/brospars/mkdocs-page-pdf/blob/master/CHANGELOG.md).


## Special Thanks
This plugin was inspired by:
- [mkdocs-with-pdf](https://github.com/orzih/mkdocs-with-pdf)
- [mkdocs-pdf-export-plugin](https://github.com/zhaoterryy/mkdocs-pdf-export-plugin)

Unlike these plugins, **mkdocs-page-pdf** uses **Playwright** (Chromium headless) for rendering, ensuring the PDF output closely matches what you see in your browser.
