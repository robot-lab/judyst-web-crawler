from setuptools import setup, find_packages
from os.path import join, dirname
import web_crawler

setup(
    name='web_crawler',
    version=web_crawler.__version__,
    packages=find_packages(),
    long_description="No description",
    # long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'pdfminer.six==20170720',
        'lxml==4.2.5',
        'selenium==3.14.1'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts':
            ['web_crawler = web_crawler.__main__:main']
        }
)
