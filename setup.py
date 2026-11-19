import io

from setuptools import find_packages, setup

setup(
    name='mkdocs-page-pdf',
    version='0.6.0',
    description='MkDocs plugin to export pages to PDF: one PDF per page with a download button, or a single combined PDF of the whole site, rendered with headless Chromium (Playwright)',
    long_description=io.open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    keywords='mkdocs mkdocs-plugin pdf pdf-export pdf-generation export documentation playwright chromium headless material',
    url='https://github.com/brospars/mkdocs-page-pdf',
    project_urls={
        'Source': 'https://github.com/brospars/mkdocs-page-pdf',
        'Issues': 'https://github.com/brospars/mkdocs-page-pdf/issues',
        'Changelog': 'https://github.com/brospars/mkdocs-page-pdf/blob/master/CHANGELOG.md',
    },
    author='brospars',
    author_email='',
    license='MIT',
    python_requires='>=3.9',
    install_requires=[
        'mkdocs>=1.1',
        'playwright>=1.57',
        'pypdf>=3.0',
        'asyncio>=1.5'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: MkDocs',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Documentation',
        'Topic :: Printing',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.plugins': [
            'page-to-pdf = mkdocs_page_pdf.plugin:PageToPdfPlugin'
        ]
    }
)