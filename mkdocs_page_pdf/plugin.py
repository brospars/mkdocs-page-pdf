import asyncio
import os
import tempfile
from pyppeteer import launch
from mkdocs.plugins import BasePlugin


class PageToPdfPlugin(BasePlugin):

    def __init__(self):
        self.browser = None
        self.page = None
        self.enabled = True

    async def page_to_pdf (self, output_content, outputpath, filename):
        # To load properly html contents need to be written to a file so we use a temporary html file
        with tempfile.NamedTemporaryFile(suffix='.html', dir=outputpath) as temp:
            temp.write(bytes(output_content, encoding='utf-8'))
            await self.page.goto('file://' + temp.name)
            await self.page.pdf({
                'path': os.path.join(outputpath, filename),
                'printBackground': True,
                'format': "A4",
                'margin': {
                    'top': "20px",
                    'bottom': "40px",
                    'left': "20px",
                    'right': "20px"
                }
            })

        print('Page to pdf ' + outputpath + filename)

    def on_pre_build(self, config):
        print('Open browser')
        self.browser = asyncio.get_event_loop().run_until_complete(launch())
        self.page = asyncio.get_event_loop().run_until_complete(self.browser.newPage())

    def on_post_page(self, output_content, page, config):
        if not self.enabled:
            return output_content
        abs_dest_path = page.file.abs_dest_path
        src_path = page.file.src_path

        path = os.path.dirname(abs_dest_path)
        os.makedirs(path, exist_ok=True)

        filename = os.path.splitext(os.path.basename(src_path))[0]
        pdf_filename = filename + '.pdf'

        asyncio.get_event_loop().run_until_complete(self.page_to_pdf(output_content, path, pdf_filename))
        return output_content

    def on_post_build(self, config):
        print('Close browser')
        asyncio.get_event_loop().run_until_complete(self.browser.close())
