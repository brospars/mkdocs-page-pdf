# Changelog

## 0.6.0 (2026-11-19)

- Add `combined` option to generate a single PDF of the whole site, in navigation order, with a bookmark for each page.
- Add `coverTemplate` option for the cover page of the combined PDF (default: theme logo and site name).
- Continuous page numbers (`pageNumber` / `totalPages`) in the headers and footers of the combined PDF.
- Add `combinedExclude` option to leave pages out of the combined PDF only.
- Add `combinedOnly` option to generate only the combined PDF.
- `headerTemplate`, `footerTemplate` and `coverTemplate` can be paths to external `.html` files.
- New dependency: `pypdf`.

## 0.5.0 (2026-11-19)

- Render pages in parallel with a bounded number of Chromium tabs (`concurrency` option), to speed up builds without running out of memory in CI.
- Fix memory leak: browser tabs were never closed.
- Fix the browser not being closed at the end of the build.
- Replace the deprecated `asyncio.get_event_loop()` and remove the `nest_asyncio` dependency.

## 0.4.0 (2025-12-18)

- Replace pyppeteer by Playwright.
- Revert parallel rendering (it could crash CI runners).
- Better error handling: a page that fails to load or render no longer stops the build.

## 0.3.0 (2025-03-28)

- Run PDF rendering in parallel.

## 0.2.1 (2025-03-28)

- Allow Jinja (mustache) templates in the download link.

## 0.2.0 (2025-03-28)

- Add customizable download button (`downloadLink` option).

## 0.1.1 (2023-02-08)

- Fix `disableOnServe` when `site_url` is not set.
- Document the blank page issue fix.

## 0.1.0 (2022-03-22)

- Fix footer template.

## 0.0.8 (2022-03-22)

- Add support for Jinja template variables in the header and footer.
- Add `exclude` option.

## 0.0.7 (2021-11-02)

- Fix `scale` option default value.
- Add `pageLoadOptions` option.

## 0.0.6 (2021-10-20)

- Add `disable` and `disableOnServe` options.

## 0.0.5 (2021-09-23)

- Add PDF rendering options.

## 0.0.4 (2021-09-22)

- Chromium arguments to run in a Docker container.

## 0.0.3 (2021-09-22)

- First release: generate a PDF for each page and add a download link.
