import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Alhosn",
    version="0.0.3",
    author="Hamad Alafeefi",
    author_email="contactme@alafeefi.com",
    description="A simple and easy to use wrapper which is able to access user information on ALhosn API using user credentials",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DmarZX2/Alhosn_api_wrapper",
    project_urls={
        "Bug Tracker": "https://github.com/DmarZX2/Alhosn_api_wrapper/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires = [
        "setuptools>=42",
        "certifi==2022.5.18.1",
        "charset-normalizer==2.0.12",
        "colorama==0.4.4",
        "colorlog==6.6.0",
        "fake-useragent==0.1.11",
        "idna==3.3",
        "phonenumbers==8.12.49",
        "requests==2.27.1",
        "urllib3==1.26.9"
    ]
)
