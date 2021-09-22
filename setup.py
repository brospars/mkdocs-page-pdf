import io

from setuptools import find_packages, setup

setup(
    name='mkdocs-page-pdf',
    version='0.0.3',
    description='Generate a PDF file for each MkDocs page',
    long_description=io.open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    keywords='mkdocs pdf pyppeteer chrome headless page',
    url='https://github.com/brospars/mkdocs-page-pdf',
    author='brospars',
    author_email='',
    license='MIT',
    python_requires='>=3.6',
    install_requires=[
        'mkdocs>=1.1',
        'pyppeteer>=0.2',
        'asyncio>=1.5',
        'nest-asyncio>=1.5'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.plugins': [
            'page-to-pdf = mkdocs_page_pdf.plugin:PageToPdfPlugin'
        ]
    }
)