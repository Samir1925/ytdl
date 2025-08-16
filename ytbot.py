import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 🔑 Replace with your bot token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

DOWNLOAD_DIR = "/data/data/com.termux/files/home/storage/downloads"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a YouTube link and I’ll download it for you!")

# Handle YouTube links
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Please send a valid YouTube link.")
        return

    await update.message.reply_text("⏳ Downloading... Please wait.")

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "format": "mp4/best",
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_text("✅ Download complete! Uploading...")
        await update.message.reply_video(video=open(filename, "rb"), caption=info.get("title"))

        os.remove(filename)  # delete after sending

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
