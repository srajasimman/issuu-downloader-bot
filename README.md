# Issuu Downloader Bot

A Telegram bot to download [Issuu](https://issuu.com) documents as PDFs. Built with Python, this bot allows users to send Issuu document URLs and receive the corresponding PDF files.

## Features
- Download Issuu documents as PDF via Telegram
- Batch download from file or single URL
- Docker and Docker Compose support for easy deployment

## Requirements
- Python 3.13+
- Telegram Bot Token (from @BotFather)
- Docker (optional, for containerized deployment)

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/srajasimman/issuu-downloader-bot.git
cd issuu-downloader-bot
```

### 2. Install dependencies (locally)
```bash
# Install uv for dependency management
curl -sSLf https://astral.sh/uv/install.sh | bash
uv sync --locked
```

### 3. Set up environment variables
Create a `.env` file with:
```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### 4. Run the bot
```bash
uv run main.py bot
```

### 5. Download from URL or file
```bash
uv run main.py --url <issuu_url> --output_dir downloads
uv run main.py --file downloads.txt --output_dir downloads
```

## Docker Usage

### Build and run with Docker Compose
```bash
docker compose up --build
```

- Place your `.env` file in the project root.
- Downloaded PDFs will be saved in the `downloads/` directory (mounted as a volume).

## File Structure
- `main.py` - Main bot and CLI logic
- `pyproject.toml` - Python dependencies
- `Dockerfile` - Container build instructions
- `docker-compose.yml` - Multi-container orchestration
- `downloads.txt` - Example file with Issuu URLs

## License
MIT License. See [LICENSE](LICENSE).

## Author
[S Rajasimman](https://github.com/srajasimman)
