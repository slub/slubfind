import setuptools

setuptools.setup(
    name="slubfind",
    version="0.0.0",
    author="Donatus Herre",
    author_email="donatus.herre@slub-dresden.de",
    description="Export data via SLUB-find.",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    license="GPLv3",
    url="https://github.com/herreio/slubfind",
    packages=["slubfind"],
    install_requires=[
        'txpyfind @ git+https://github.com/herreio/txpyfind#egg=txpyfind'
    ],
)
