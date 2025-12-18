# Mkdocs Page to PDF

An MkDocs plugin to generate a PDF file for each MkDocs page using **Playwright** (Chromium headless) and add a download button.


## How to Use

### 1. Install the Package
Install the plugin using pip:

```shell
pip install mkdocs-page-pdf
```

Then, install Playwright browsers:

```shell
playwright install
```


### 2. Enable the Plugin
Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  # - ...
  - page-to-pdf  # Should be last to ensure all content is rendered
```


### Options
To customize the plugin, use the following options in your `mkdocs.yml`:

```yaml
plugins:
  # - ...
  - page-to-pdf:
      # Options here
```

#### General Options
- **`disable`** (bool): Disable PDF rendering. Useful for quickly disabling the plugin without removing its configuration. Default: `False`.
- **`disableOnServe`** (bool): Disable PDF rendering when using `mkdocs serve`. Default: `False`.

#### PDF Rendering Options
The following options are based on [Playwright's PDF generation capabilities](https://playwright.dev/python/docs/api/class-page#page-pdf):

- **`scale`** (float): Scale of the webpage rendering. Default: `1.0`.
- **`displayHeaderFooter`** (bool): Display header and footer. Default: `False`.
- **`headerTemplate`** (str): HTML template for the print header. Use the following classes:
  - `date`: Formatted print date
  - `title`: Document title
  - `url`: Document location
  - `pageNumber`: Current page number
  - `totalPages`: Total pages in the document
- **`footerTemplate`** (str): HTML template for the print footer. Same classes as `headerTemplate`.
- **`printBackground`** (bool): Print background graphics. Default: `False`.
- **`landscape`** (bool): Use landscape orientation. Default: `False`.
- **`pageRanges`** (str): Page ranges to print (e.g., `'1-5, 8, 11-13'`). Default: `""` (all pages).
- **`format`** (str): Paper format. Default: `"A4"`.
- **`margin`** (dict): Paper margins. Default:
  ```yaml
  margin:
    top: "20px"
    right: "20px"
    bottom: "20px"
    left: "20px"
  ```
- **`pageLoadOptions`** (dict): Page load options (see [Playwright's `page.goto`](https://playwright.dev/python/docs/api/class-page#page-goto)).
  - **`timeout`** (int): Maximum navigation time in milliseconds. Default: `30000`.
  - **`waitUntil`** (str): When to consider navigation successful. Default: `"load"`.
- **`exclude`** (list): List of glob patterns to exclude from PDF generation.
- **`downloadLink`** (str): Custom HTML for the PDF download link. Default: SVG icon for PDF.


## Troubleshooting

### Running in a Docker Container (CI/CD)
If you encounter issues running Playwright in Docker (e.g., `Browser closed unexpectedly`), you may need to install additional system dependencies for Chromium.

#### Recommended Docker Image
Use a ready-to-use Docker image with all dependencies pre-installed:
- [brospars/docker-mkdocs](https://github.com/brospars/docker-mkdocs)

#### Manual Setup
If you prefer to set up your own image, refer to:
- [Playwright Docker Guide](https://playwright.dev/docs/docker)
- [Puppeteer Troubleshooting in Docker](https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md#running-puppeteer-in-docker)


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


## Special Thanks
This plugin was inspired by:
- [mkdocs-with-pdf](https://github.com/orzih/mkdocs-with-pdf)
- [mkdocs-pdf-export-plugin](https://github.com/zhaoterryy/mkdocs-pdf-export-plugin)

Unlike these plugins, **mkdocs-page-pdf** uses **Playwright** (Chromium headless) for rendering, ensuring the PDF output closely matches what you see in your browser.
