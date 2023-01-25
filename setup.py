import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'beautifulsoup4 == 4.*',
    'types-beautifulsoup4 == 4.*',
    'click == 8.*',
    'jinja2 == 3.*',
    'loguru == 0.6.*',
    'pandas == 1.*',
    'pandas-stubs == 1.*',
    'playwright == 1.*',
]

DEV_REQUIREMENTS = [
    'black == 22.*',
    'build == 0.7.*',
    'flake8 == 4.*',
    'isort == 5.*',
    'mypy == 0.942',
    'pre-commit == 2.20.*',
    'pytest == 7.*',
    'pytest-cov == 4.*',
    'sphinx == 4.*',
    'sphinx-rtd-theme == 1.*',
    'twine == 4.*',
]

setuptools.setup(
    name='gdpr-website-checker-cli',
    version='0.1.0',
    description='Checks loading of external resources and cookies without consent',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/MattHag/gdpr-website-checker-cli',
    author='Matthias Hagmann',
    license='MIT',
    packages=setuptools.find_packages(
        exclude=[
            'examples',
            'test',
        ]
    ),
    package_data={
        'gdpr-website-checker-cli': [
            'py.typed',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    entry_points={
        'console_scripts': [
            'gdpr-website-checker-cli=website_checker.my_module:main',
        ]
    },
    python_requires='>=3.7, <4',
)
