import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iso15692-OLLI-ANTTI-KIVILAHTI", # Replace with your own username
    version="0.0.2",
    author="Olli-Antti Kivilahti",
    author_email="olli-antti.kivilahti@hypernova.fi",
    description="ISO 15692 compaction algorithm implementations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kivilahtio/iso15692",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
