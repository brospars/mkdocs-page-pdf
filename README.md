# Mkdocs Page to PDF

An Mkdocs plugin to generate a PDF file for each MkDocs page.

## How to use

Install the package with pip:

```shell
pip install mkdocs-page-pdf
```

Enable the plugin in your mkdocs.yml:

```yaml
plugins:
  # - ...
    - pdf-export # should be last
```

### Options

Options are directly induced from [pyppeteer options](https://pyppeteer.github.io/pyppeteer/reference.html?highlight=pdf#pyppeteer.page.Page.pdf) :

* ``scale`` (float): Scale of the webpage rendering, defaults to ``1``.
* ``displayHeaderFooter`` (bool): Display header and footer.
  Defaults to ``False``.
* ``headerTemplate`` (str): HTML template for the print header. Should
  be valid HTML markup with following classes.
  * ``date``: formatted print date
  * ``title``: document title
  * ``url``: document location
  * ``pageNumber``: current page number
  * ``totalPages``: total pages in the document
* ``footerTemplate`` (str): HTML template for the print footer. Should use the same template as ``headerTemplate``.
* ``printBackground`` (bool): Print background graphics. Defaults to``False``.
* ``landscape`` (bool): Paper orientation. Defaults to ``False``.
* ``pageRanges`` (string): Paper ranges to print, e.g., '1-5,8,11-13'. Defaults to empty string, which means all pages.
* ``format`` (str): Paper format. Defaults to ``A4``.
* ``margin`` (dict): Paper margins.
  * ``top`` (str): Top margin, accepts values labeled with units, defaults to ``20px``.
  * ``right`` (str): Right margin, accepts values labeled with units, defaults to ``20px``.
  * ``bottom`` (str): Bottom margin, accepts values labeled with units, defaults to ``20px``.
  * ``left`` (str): Left margin, accepts values labeled with units, defaults to ``20px``.


