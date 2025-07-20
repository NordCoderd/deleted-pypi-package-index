# Deleted & Revived PyPI Package Indexes

This project contains data about deleted and revived package names from PyPI.org and updates on a daily schedule.

Initial data about deleted packages was received by analyzing historical data on [clickpy](https://clickpy.clickhouse.com/) and the current state of PyPI.org. Data about deleted packages before 21 July 2025 could have false positives.  
Read more about the methodology of retrieving these names in the article: [Revival Hijacking: How Deleted PyPI Packages Become Threats](https://protsenko.dev/2025/07/21/revival-hijacking-how-deleted-pypi-packages-become-threats/)

## Project Structure

1. [latest-pypi-state.txt](pypi-uploader-directory/latest-pypi-state.txt) contains the list of currently registered projects.
2. [deleted-pypi-packages.txt](pypi-uploader-directory/deleted-pypi-packages.txt) contains the list of deleted packages received via analysis of the current state of PyPI.org and the previous one.
3. [revived-pypi-packages.txt](pypi-uploader-directory/revived-pypi-packages.txt) contains the list of revived packages. It could be a signal of a [revival-hijacking](https://protsenko.dev/2025/07/21/revival-hijacking-how-deleted-pypi-packages-become-threats/) attack or legal cases.

## How to Use

You can use these lists to cross-check artifacts stored in your internal package repositories or the dependency information in your projects to identify deleted or revived packages and mitigate revival-hijacking risks.

Use these links to download fresh lists:
```
https://raw.githubusercontent.com/NordCoderd/deleted-pypi-package-index/refs/heads/main/pypi-uploader-directory/deleted-pypi-packages.txt
https://raw.githubusercontent.com/NordCoderd/deleted-pypi-package-index/refs/heads/main/pypi-uploader-directory/revived-pypi-packages.txt
```