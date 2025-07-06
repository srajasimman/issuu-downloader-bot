import os
import re
import logging
import tempfile
import requests
import img2pdf
import argparse
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()  # Load environment variables from .env file

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Issuu Downloader Logic (adapted from main.py) ---
def download_issuu_pdf(url, output_path):
    match = re.search(r'issuu\.com/([^/]+)/docs/([^/]+)', url)
    if not match:
        raise ValueError("Invalid Issuu document URL format.")
    username, document_id = match.groups()
    json_url = f"https://reader3.isu.pub/{username}/{document_id}/reader3_4.json"
    response = requests.get(json_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch JSON data. Status code: {response.status_code}")
    data = response.json()
    pages = data.get('document', {}).get('pages', [])
    if not pages:
        raise Exception("No pages found in the document data.")
    with tempfile.TemporaryDirectory() as temp_dir:
        image_files = []
        for i, page in enumerate(pages):
            image_url = page.get('imageUri')
            if not image_url:
                continue
            img_resp = requests.get('https://' + image_url)
            if img_resp.status_code == 200:
                img_path = os.path.join(temp_dir, f'page_{i+1}.jpg')
                with open(img_path, 'wb') as f:
                    f.write(img_resp.content)
                image_files.append(img_path)
        if not image_files:
            raise Exception("No pages were successfully downloaded.")
        with open(output_path, 'wb') as f:
            f.write(img2pdf.convert(image_files))

# --- Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me an Issuu document URL and I'll download the PDF for you!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    match = re.search(r'issuu\.com/([^/]+)/docs/([^/]+)', url)
    if not match:
        await update.message.reply_text("Please send a valid Issuu document URL.")
        return
    await update.message.reply_text("Downloading your document, please wait...")
    username, document_id = match.groups()
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            tmp_pdf.name = f"{username}_{document_id}.pdf"
            download_issuu_pdf(url, tmp_pdf.name)
            await update.message.reply_document(document=open(tmp_pdf.name, "rb"))
        os.remove(tmp_pdf.name)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"Failed to download: {e}")

def bot():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Please set the TELEGRAM_BOT_TOKEN environment variable.")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling(poll_interval=5)

def download_from_file(file_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(file_path, 'r') as file:
        urls = file.readlines()
    for url in urls:
        url = url.strip()
        if not url:
            continue
        try:
            match = re.search(r'issuu\.com/([^/]+)/docs/([^/]+)', url)
            if not match:
                print(f"Invalid URL format: {url}")
                continue
            username, document_id = match.groups()
            output_path = os.path.join(output_dir, f"{username}_{document_id}.pdf")
            download_issuu_pdf(url, output_path)
            print(f"Downloaded: {output_path}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")

def download_from_url(url, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        match = re.search(r'issuu\.com/([^/]+)/docs/([^/]+)', url)
        if not match:
            print(f"Invalid URL format: {url}")
            return
        username, document_id = match.groups()
        output_path = os.path.join(output_dir, f"{username}_{document_id}.pdf")
        download_issuu_pdf(url, output_path)
        print(f"Downloaded: {output_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Issuu documents as PDFs.")
    parser.add_argument('bot', nargs='?', help="Run the Telegram bot if specified")
    parser.add_argument('--url', help="Issuu document URL or path to a file containing URLs", default=None, required=False)
    parser.add_argument('--file', help="Path to a file containing Issuu URLs", default=None, required=False)
    parser.add_argument('--output_dir', help="Directory to save the downloaded PDFs", default='downloads', required=False)
    args = parser.parse_args()

    if args.bot:
        bot()
    elif args.url or args.file:
        output_dir = args.output_dir
        if args.file:
            download_from_file(args.file, output_dir)
        elif args.url:
            download_from_url(args.url, output_dir)
    else:
        print("Please provide a URL or a file containing URLs, or run the bot with 'python main.py bot'.")
        parser.print_help()