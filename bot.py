from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import pandas as pd
import re
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
EXCEL_FILE = "case_log.xlsx"


def extract(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    return pd.DataFrame(columns=[
        "Case No",
        "Date Time",
        "Rank/Name",
        "Service",
        "Brief Description",
        "Temperature",
        "AVPU",
        "Incident Location",
        "Resting Location"
    ])


def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "Case Number" not in text:
        await update.message.reply_text("❌ Invalid format: missing Case Number")
        return

    row = {
        "Case No": extract(r"Case Number\s*:\s*(.*)", text),
        "Date Time": extract(r"Date & Time\s*:\s*(.*)", text),
        "Rank/Name": extract(r"RANK/NAME\s*:\s*(.*)", text),
        "Service": extract(r"SERVICE/UNIT\s*:\s*(.*)", text),
        "Brief Description": extract(r"Brief Description\s*:\s*(.*)", text),
        "Temperature": extract(r"Temperature\s*:\s*(.*)", text),
        "AVPU": extract(r"AVPU\s*:\s*(.*)", text),
        "Incident Location": extract(r"Location of Incident\s*:\s*(.*)", text),
        "Resting Location": extract(r"Location Casualty Resting at\s*:\s*(.*)", text),
    }

    df = load_data()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_data(df)

    await update.message.reply_text(f"✅ Case {row['Case No']} saved")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
