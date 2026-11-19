import asyncio
import io
import os
import tempfile
from pathlib import PurePath
from playwright.async_api import async_playwright
from pypdf import PdfReader, PdfWriter
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from jinja2 import Template

DEFAULT_CONCURRENCY = min(4, os.cpu_count() or 1)
DEFAULT_COVER_TEMPLATE = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: sans-serif; text-align: center; padding-top: 25vh">
  {% if config.theme.logo %}<img src="{{ config.theme.logo }}" width="120">{% endif %}
  <h1>{{ config.site_name }}</h1>
</body>
</html>"""

class PageToPdfPlugin(BasePlugin):
    config_scheme = (
        ('disable', config_options.Type(bool, default=False)),
        ('disableOnServe', config_options.Type(bool, default=False)),
        ('concurrency', config_options.Type(int, default=DEFAULT_CONCURRENCY)),
        ('scale', config_options.Type(float, default=1.0)),
        ('printBackground', config_options.Type(bool, default=False)),
        ('displayHeaderFooter', config_options.Type(bool, default=False)),
        ('headerTemplate', config_options.Type(str, default="")),
        ('footerTemplate', config_options.Type(str, default="")),
        ('combined', config_options.Type(bool, default=False)),
        ('combinedFilename', config_options.Type(str, default="combined.pdf")),
        ('combinedExclude', config_options.Type(list, default=[])),
        ('combinedOnly', config_options.Type(bool, default=False)),
        ('coverTemplate', config_options.Type(str, default=DEFAULT_COVER_TEMPLATE)),
        ('landscape', config_options.Type(bool, default=False)),
        ('pageRanges', config_options.Type(str, default="")),
        ('format', config_options.Type(str, default="A4")),
        ('margin', config_options.Type(dict, default={'top': "20px", 'bottom': "20px", 'left': "20px", 'right': "20px"})),
        ('pageLoadOptions', config_options.Type(dict, default={'timeout': 30000, 'waitUntil': "load"})),
        ('exclude', config_options.Type(list, default=[])),
        ('downloadLink', config_options.Type(str, default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 10.5h1v3h-1v-3m-5 1h1v-1H7v1M20 6v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2M9.5 10.5A1.5 1.5 0 0 0 8 9H5.5v6H7v-2h1a1.5 1.5 0 0 0 1.5-1.5v-1m5 0A1.5 1.5 0 0 0 13 9h-2.5v6H13a1.5 1.5 0 0 0 1.5-1.5v-3m4-1.5h-3v6H17v-2h1.5v-1.5H17v-1h1.5V9z"></path></svg>')),
    )

    def __init__(self):
        self.loop = None
        self.browser = None
        self.tasks = []
        self.pdf_files = {}
        self.header_footers = {}
        self.nav = None
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
        if self.config['combinedOnly']:
            self.config['combined'] = True
        config_dir = os.path.dirname(config['config_file_path'] or '')
        for key in ('headerTemplate', 'footerTemplate', 'coverTemplate'):
            template_path = os.path.join(config_dir, self.config[key])
            if self.config[key].endswith('.html') and os.path.isfile(template_path):
                with open(template_path, encoding='utf-8') as f:
                    self.config[key] = f.read()
        return config

    def on_pre_build(self, config):
        self.tasks = []
        self.pdf_files = {}
        self.header_footers = {}
        if self.config['disable']:
            return

        async def _launch_browser():
            try:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
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
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(_launch_browser())

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
                    if self.config['combined'] and self.config['displayHeaderFooter']:
                        await page.pdf(
                            path=os.path.join(outputpath, filename) + '.body',
                            scale=self.config['scale'],
                            print_background=self.config['printBackground'],
                            landscape=self.config['landscape'],
                            page_ranges=self.config['pageRanges'],
                            format=self.config['format'],
                            margin=self.config['margin']
                        )
                        self.header_footers[os.path.join(outputpath, filename)] = (header_template, footer_template, await page.title())
                except Exception as e:
                    print(f"Warning: PDF render failed for {temp_path}: {e}")
                    return
            finally:
                await page.close()
                os.unlink(temp_path)
            if os.path.exists(os.path.join(outputpath, filename)):
                print(f"PDF generated: {os.path.join(outputpath, filename)}")

        self.tasks.append(_generate_pdf())

    async def render_cover(self, config):
        output_content = Template(self.config['coverTemplate']).render(config=config, nav=self.nav)
        with tempfile.NamedTemporaryFile(suffix='.html', dir=config['site_dir'], delete=False) as temp:
            temp.write(bytes(output_content, encoding='utf-8'))
            temp_path = temp.name
        cover_path = temp_path[:-len('.html')] + '.pdf'

        page = await self.browser.new_page()
        try:
            await page.goto(
                f'file://{temp_path}',
                wait_until=self.config['pageLoadOptions']['waitUntil'],
                timeout=self.config['pageLoadOptions']['timeout']
            )
            await page.pdf(
                path=cover_path,
                scale=self.config['scale'],
                print_background=self.config['printBackground'],
                landscape=self.config['landscape'],
                format=self.config['format'],
                margin=self.config['margin']
            )
            return cover_path
        except Exception as e:
            print(f"Warning: Cover render failed: {e}")
            return None
        finally:
            await page.close()
            os.unlink(temp_path)

    async def combine_pdfs(self, config):
        output_dir = config['site_dir']
        if self.nav and self.nav.homepage:
            output_dir = os.path.dirname(self.nav.homepage.file.abs_dest_path)
        output_path = os.path.join(output_dir, self.config['combinedFilename'])
        cover_path = await self.render_cover(config) if self.config['coverTemplate'] else None
        writer = PdfWriter()
        overlay_page = None
        try:
            if cover_path:
                writer.append(cover_path)
            parts = []
            for page in self.nav.pages if self.nav else []:
                if not self.in_combined(page):
                    continue
                pdf_path = self.pdf_files.get(page.file.src_path)
                if pdf_path and os.path.exists(pdf_path):
                    parts.append((page.title, pdf_path, self.header_footers.get(pdf_path)))
            if not self.header_footers:
                for title, pdf_path, _ in parts:
                    writer.append(pdf_path, outline_item=title)
            else:
                readers = [PdfReader(pdf_path + '.body' if header_footer else pdf_path) for _, pdf_path, header_footer in parts]
                total = sum(len(reader.pages) for reader in readers)
                overlay_page = await self.browser.new_page()
                await overlay_page.set_content('<div style="height: 1px; break-after: page"></div>' * total)
                offset = 0
                for (title, pdf_path, header_footer), reader in zip(parts, readers):
                    overlay = None
                    if header_footer:
                        overlay = PdfReader(io.BytesIO(await self.render_header_footer(overlay_page, header_footer, offset, len(reader.pages))))
                    first_page = len(writer.pages)
                    for i, body_page in enumerate(reader.pages):
                        added_page = writer.add_page(body_page)
                        if overlay:
                            added_page.merge_page(overlay.pages[i])
                    writer.add_outline_item(title=title, page_number=first_page)
                    offset += len(reader.pages)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            writer.write(output_path)
            print(f"Combined PDF generated: {output_path}")
        except Exception as e:
            print(f"Warning: Combined PDF failed: {e}")
        finally:
            writer.close()
            if overlay_page:
                await overlay_page.close()
            if cover_path:
                os.unlink(cover_path)
            for pdf_path in self.header_footers:
                if os.path.exists(pdf_path + '.body'):
                    os.unlink(pdf_path + '.body')
            if self.config['combinedOnly']:
                for pdf_path in self.pdf_files.values():
                    if os.path.exists(pdf_path):
                        os.unlink(pdf_path)

    def in_combined(self, page):
        if self.nav and page.file.src_path not in [nav_page.file.src_path for nav_page in self.nav.pages]:
            return False
        return not any(PurePath(page.file.src_path).match(pattern) for pattern in self.config['combinedExclude'])

    async def render_header_footer(self, page, header_footer, offset, count):
        header_template, footer_template, title = header_footer
        await page.evaluate('title => document.title = title', title)
        return await page.pdf(
            scale=self.config['scale'],
            display_header_footer=True,
            header_template=header_template,
            footer_template=footer_template,
            landscape=self.config['landscape'],
            page_ranges=f'{offset + 1}-{offset + count}',
            format=self.config['format'],
            margin=self.config['margin']
        )

    def add_link(self, output_content, url):
        icon = self.download_link
        link = f'<a class="md-content__button md-icon" download href="{url}" title="PDF">{icon}</a>'
        output_content = output_content.replace('<article class="md-content__inner md-typeset">', '<article class="md-content__inner md-typeset">' + link)
        return output_content

    def on_nav(self, nav, config, files):
        self.nav = nav
        return nav

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
        if self.config['combinedOnly'] and not self.in_combined(page):
            return output_content

        abs_dest_path = page.file.abs_dest_path
        src_path = page.file.src_path
        path = os.path.dirname(abs_dest_path)
        os.makedirs(path, exist_ok=True)
        filename = os.path.splitext(os.path.basename(src_path))[0]
        pdf_filename = filename + '.pdf'

        self.page_to_pdf(output_content, path, pdf_filename)
        self.pdf_files[src_path] = os.path.join(path, pdf_filename)
        if not self.config['combinedOnly']:
            output_content = self.add_link(output_content, pdf_filename)
        return output_content

    def on_post_build(self, config):
        if self.config['disable'] or self.browser is None:
            return

        async def _run_tasks():
            semaphore = asyncio.Semaphore(max(1, self.config['concurrency']))

            async def _limited(task):
                async with semaphore:
                    await task

            await asyncio.gather(*(_limited(task) for task in self.tasks))

        self.loop.run_until_complete(_run_tasks())
        if self.config['combined']:
            self.loop.run_until_complete(self.combine_pdfs(config))

        async def _close_browser():
            try:
                await self.browser.close()
                await self.playwright.stop()
                print("Browser closed successfully.")
            except Exception as e:
                print(f"Warning: Failed to close browser: {e}")

        self.loop.run_until_complete(_close_browser())
        self.loop.close()
