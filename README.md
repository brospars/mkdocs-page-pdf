# Mkdocs Page to PDF

An Mkdocs plugin to generate a PDF file for each MkDocs page using `pyppeteer` (chrome headless) 
and add a download button.

## How to use

Install the package with pip:

```shell
pip install mkdocs-page-pdf
```

Enable the plugin in your mkdocs.yml:

```yaml
plugins:
  # - ...
    - page-to-pdf # should be last
```

### Options
To set different options use the following syntax.
```yaml
plugins:
  # - ...
    - page-to-pdf :
        # Options here
```
* ``disable`` (bool): Disable pdf rendering useful to quickly disable it without removing the plugin config. Defaults to ``False``.
* ``disableOnServe`` (bool): Disable pdf rendering when using `mkdocs serve`. Defaults to ``False``.

The following options are directly induced from [pyppeteer options](https://pyppeteer.github.io/pyppeteer/reference.html?highlight=pdf#pyppeteer.page.Page.pdf) :

* ``scale`` (float): Scale of the webpage rendering, defaults to ``1.0``.
* ``displayHeaderFooter`` (bool): Display header and footer.
  Defaults to ``False``.
* ``headerTemplate`` (str): HTML template for the print header. Should
  be valid HTML markup with following classes.
  * ``date``: formatted print date
  * ``title``: document title
  * ``url``: document location
  * ``pageNumber``: current page number
  * ``totalPages``: total pages in the document
* ``footerTemplate`` (str): HTML template for the print footer. Should be valid HTML markup with the same classes as ``headerTemplate``.
* ``printBackground`` (bool): Print background graphics. Defaults to``False``.
* ``landscape`` (bool): Paper orientation. Defaults to ``False``.
* ``pageRanges`` (string): Paper ranges to print, e.g., '1-5,8,11-13'. Defaults to empty string, which means all pages.
* ``format`` (str): Paper format. Defaults to ``A4``.
* ``margin`` (dict): Paper margins.
  * ``top`` (str): Top margin, accepts values labeled with units, defaults to ``20px``.
  * ``right`` (str): Right margin, accepts values labeled with units, defaults to ``20px``.
  * ``bottom`` (str): Bottom margin, accepts values labeled with units, defaults to ``20px``.
  * ``left`` (str): Left margin, accepts values labeled with units, defaults to ``20px``.
* ``pageLoadOptions`` (dict): Page load options (see [this](https://pyppeteer.github.io/pyppeteer/reference.html?highlight=goto#pyppeteer.page.Page.goto)).
  * ``timeout`` (int): Maximum time in milliseconds, defaults to ``30000``.
  * ``waitUntil`` (str): When to consider navigation succeeded, defaults to ``load``.
* ``exclude`` (list) : List of glob pattern to exclude

### Troubleshooting

#### Running in a docker container (ci/cd) 

Depending on what image you are using you may encounter some issue running `pyppeteer` : `Browser closed unexpectedly`
This is due to some missing shared librairies used by Chrome Headless. 

Related issue : https://github.com/pyppeteer/pyppeteer/issues/194  
See this [article](https://www.cloudsavvyit.com/13461/how-to-run-puppeteer-and-headless-chrome-in-a-docker-container/)
and this [guide](https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md#running-puppeteer-in-docker)  
Ready-to-use docker image : https://github.com/brospars/docker-mkdocs

#### Slow build on serve

You can use `disable` or `disableOnServe` options to disable the pdf rendering (entirely or on serve) but you can also 
use the `mkdocs serve --dirtyreload` flag to only rebuild modified files on the fly.

#### Blank page at the end

Due to a [chrome bug](https://github.com/brospars/mkdocs-page-pdf/issues/9) a blank page can appear at the end of the PDF you can remove it by addin the following to you extra.css :

```css
@media print {
    body { contain: content; }
}
```

## Special thanks

This plugin was inspired by [mkdocs-with-pdf](https://github.com/orzih/mkdocs-with-pdf)
and [mkdocs-pdf-export-plugin](https://github.com/zhaoterryy/mkdocs-pdf-export-plugin)
but without using `weasyprint` and instead `pyppeteer` (chrome headless) to have a render 
closer to what you have in your chrome browser.

