# Devilsect Downloader
Download every novel available in devilsect as an EPUB.

## How to run

### Docker
1. .env file
    > mv .env.example .env
    - update the variables accordingly

2. docker compose up -d --build

### From source
1. .env file
    > mv .env.example .env
    - update the variables accordingly

2. run the project
> uv run downloader

> OBS: Make sure that the database and rabbitmq are up