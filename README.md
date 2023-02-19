<div align="center">

# GDPR Website Checker with CLI

Checks loading of external resources and cookies without consent.

[![Build Status](https://github.com/MattHag/gdpr-website-checker-cli/workflows/build/badge.svg)](https://github.com/MattHag/gdpr-website-checker-cli/actions)
[![Coverage Status](https://coveralls.io/repos/github/MattHag/gdpr-website-checker-cli/badge.svg?branch=main&t=o2BiJf)](https://coveralls.io/github/MattHag/gdpr-website-checker-cli?branch=main)
[![PyPi](https://img.shields.io/pypi/v/gdpr-website-checker-cli)](https://pypi.org/project/gdpr-website-checker-cli)
[![Licence](https://img.shields.io/github/license/MattHag/gdpr-website-checker-cli)](LICENSE)

</div>

A longer paragraph description of your project goes here.

## Install

```bash
# Install tool
pip3 install website_checker

# Install locally
make install
```

## Update cookie database

The update scripts loads the newest Cookie data CSV file (from https://github.com/jkwakman/Open-Cookie-Database) and
checks its compatibility. If the new file is compatible, it will be used as the new database.

```bash
make update
```

Manually replacing is also possible. Just replace the file _open-cookie-database.csv_ with the new one. However, that
might cause a failure if the new file is not compatible.

## Usage

Usage instructions go here.

```bash
venv/bin/python my_script.py
```

## Development

```bash
# Get a comprehensive list of development tools
make help
```
