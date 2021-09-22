import asyncio
import os
import tempfile
import nest_asyncio
from pyppeteer import launch
from mkdocs.plugins import BasePlugin


nest_asyncio.apply()


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

        print('Page to pdf ' + os.path.join(outputpath, filename))

    def on_pre_build(self, config):
        try:
            print('Run headless browser for pdf rendering')
            self.browser = asyncio.get_event_loop().run_until_complete(launch())
            self.page = asyncio.get_event_loop().run_until_complete(self.browser.newPage())
        except RuntimeError:
            print(asyncio.all_tasks())

    def add_link(self, output_content, url):
        icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 10.5h1v3h-1v-3m-5 1h1v-1H7v1M20 6v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2M9.5 10.5A1.5 1.5 0 0 0 8 9H5.5v6H7v-2h1a1.5 1.5 0 0 0 1.5-1.5v-1m5 0A1.5 1.5 0 0 0 13 9h-2.5v6H13a1.5 1.5 0 0 0 1.5-1.5v-3m4-1.5h-3v6H17v-2h1.5v-1.5H17v-1h1.5V9z"></path></svg>'
        link = '<a class="md-content__button md-icon" download href="'+ url +'" title="PDF">' + icon + '</a>'
        output_content = output_content.replace('<article class="md-content__inner md-typeset">', '<article class="md-content__inner md-typeset">' + link)

        return output_content

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

        output_content = self.add_link(output_content, pdf_filename)
        return output_content

    def on_post_build(self, config):
        print('Close headless browser')
        asyncio.get_event_loop().run_until_complete(self.browser.close())
