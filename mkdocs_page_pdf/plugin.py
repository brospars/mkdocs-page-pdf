import asyncio
import os
import tempfile
import nest_asyncio
from pathlib import PurePath
from playwright.async_api import async_playwright
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from jinja2 import Template

nest_asyncio.apply()

class PageToPdfPlugin(BasePlugin):
    config_scheme = (
        ('disable', config_options.Type(bool, default=False)),
        ('disableOnServe', config_options.Type(bool, default=False)),
        ('scale', config_options.Type(float, default=1.0)),
        ('printBackground', config_options.Type(bool, default=False)),
        ('displayHeaderFooter', config_options.Type(bool, default=False)),
        ('headerTemplate', config_options.Type(str, default="")),
        ('footerTemplate', config_options.Type(str, default="")),
        ('landscape', config_options.Type(bool, default=False)),
        ('pageRanges', config_options.Type(str, default="")),
        ('format', config_options.Type(str, default="A4")),
        ('margin', config_options.Type(dict, default={'top': "20px", 'bottom': "20px", 'left': "20px", 'right': "20px"})),
        ('pageLoadOptions', config_options.Type(dict, default={'timeout': 30000, 'waitUntil': "load"})),
        ('exclude', config_options.Type(list, default=[])),
        ('downloadLink', config_options.Type(str, default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 10.5h1v3h-1v-3m-5 1h1v-1H7v1M20 6v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2M9.5 10.5A1.5 1.5 0 0 0 8 9H5.5v6H7v-2h1a1.5 1.5 0 0 0 1.5-1.5v-1m5 0A1.5 1.5 0 0 0 13 9h-2.5v6H13a1.5 1.5 0 0 0 1.5-1.5v-3m4-1.5h-3v6H17v-2h1.5v-1.5H17v-1h1.5V9z"></path></svg>')),
    )

    def __init__(self):
        self.browser = None
        self.download_link = ''
        self.header_template = ''
        self.footer_template = ''

    def on_config(self, config):
        onServe = config['site_url'] is not None and config['dev_addr'].host+':'+str(config['dev_addr'].port) in config['site_url']
        if self.config['disable']:
            print('PDF rendering is disabled')
        if self.config['disableOnServe'] and onServe:
            print('PDF rendering is disabled in serve mode')
            self.config['disable'] = True
        return config

    def on_pre_build(self, config):
        if self.config['disable']:
            return

        async def _launch_browser():
            try:
                playwright = await async_playwright().start()
                self.browser = await playwright.chromium.launch(
                    args=[
                        "--disable-gpu",
                        "--disable-dev-shm-usage",
                        "--disable-setuid-sandbox",
                        "--no-sandbox"
                    ]
                )
                print("Browser launched successfully.")
            except Exception as e:
                print(f"Warning: Failed to launch browser: {e}")
                self.browser = None

        print("Launching browser for PDF rendering...")
        asyncio.get_event_loop().run_until_complete(_launch_browser())

    def page_to_pdf(self, output_content, outputpath, filename):
        if self.browser is None:
            print("Warning: Browser not available. Skipping PDF generation.")
            return

        header_template = self.header_template
        footer_template = self.footer_template

        with tempfile.NamedTemporaryFile(suffix='.html', dir=outputpath, delete=False) as temp:
            temp.write(bytes(output_content, encoding='utf-8'))
            temp_path = temp.name

        async def _generate_pdf():
            page = await self.browser.new_page()
            try:
                await page.goto(
                    f'file://{temp_path}',
                    wait_until=self.config['pageLoadOptions']['waitUntil'],
                    timeout=self.config['pageLoadOptions']['timeout']
                )
            except Exception as e:
                print(f"Warning: Page load timeout or error for {temp_path}: {e}")
                return

            try:
                await page.pdf(
                    path=os.path.join(outputpath, filename),
                    scale=self.config['scale'],
                    print_background=self.config['printBackground'],
                    display_header_footer=self.config['displayHeaderFooter'],
                    header_template=header_template,
                    footer_template=footer_template,
                    landscape=self.config['landscape'],
                    page_ranges=self.config['pageRanges'],
                    format=self.config['format'],
                    margin=self.config['margin']
                )
            except Exception as e:
                print(f"Warning: PDF render failed for {temp_path}: {e}")
                return

        asyncio.get_event_loop().run_until_complete(_generate_pdf())
        os.unlink(temp_path)
        if os.path.exists(os.path.join(outputpath, filename)):
            print(f"PDF generated: {os.path.join(outputpath, filename)}")

    def add_link(self, output_content, url):
        icon = self.download_link
        link = f'<a class="md-content__button md-icon" download href="{url}" title="PDF">{icon}</a>'
        output_content = output_content.replace('<article class="md-content__inner md-typeset">', '<article class="md-content__inner md-typeset">' + link)
        return output_content

    def on_page_context(self, context, page, config, nav):
        download_link = Template(self.config['downloadLink'])
        self.download_link = download_link.render(context)
        header_template = Template(self.config['headerTemplate'])
        self.header_template = header_template.render(context)
        footer_template = Template(self.config['footerTemplate'])
        self.footer_template = footer_template.render(context)
        return context

    def on_post_page(self, output_content, page, config):
        for pattern in self.config['exclude']:
            if PurePath(page.file.src_path).match(pattern):
                print(f"File excluded: {page.file.src_path} ({pattern})")
                return output_content
        if self.config['disable']:
            return output_content

        abs_dest_path = page.file.abs_dest_path
        src_path = page.file.src_path
        path = os.path.dirname(abs_dest_path)
        os.makedirs(path, exist_ok=True)
        filename = os.path.splitext(os.path.basename(src_path))[0]
        pdf_filename = filename + '.pdf'

        self.page_to_pdf(output_content, path, pdf_filename)
        output_content = self.add_link(output_content, pdf_filename)
        return output_content

    def on_post_build(self, config):
        if self.config['disable'] or self.browser is None:
            return

        async def _close_browser():
            try:
                await self.browser.stop()
                print("Browser closed successfully.")
            except Exception as e:
                print(f"Warning: Failed to close browser: {e}")

        asyncio.get_event_loop().run_until_complete(_close_browser())
