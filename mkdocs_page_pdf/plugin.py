import asyncio
import os
from pyppeteer import launch
from mkdocs.plugins import BasePlugin


class PageToPdfPlugin(BasePlugin):

    def __init__(self):
        self.enabled = True

    async def page_to_pdf (self, url, outputpath):
        browser = await launch()
        page = await browser.newPage()
        await page.goto(url)
        await page.pdf({
            'path': outputpath,
            'printBackground': True,
            'format': "A4",
            'margin': {
                'top': "20px",
                'bottom': "40px",
                'left': "20px",
                'right': "20px"
            }
        })
        await browser.close()

    def on_post_page(self, output_content, page, config):
        if not self.enabled:
            return output_content
        abs_dest_path = page.file.abs_dest_path
        src_path = page.file.src_path

        path = os.path.dirname(abs_dest_path)
        os.makedirs(path, exist_ok=True)

        filename = os.path.splitext(os.path.basename(src_path))[0]
        pdf_outputpath = os.path.join(path, filename + '.pdf')

        asyncio.get_event_loop().run_until_complete(self.page_to_pdf(page.file.url, pdf_outputpath))
