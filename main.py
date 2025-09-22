import os, time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from telegram import Update, LabeledPrice, SuccessfulPayment
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, PreCheckoutQueryHandler, filters
)

load_dotenv()
BOT_TOKEN       = os.getenv("BOT_TOKEN")
VIP_CHAT_ID     = int(os.getenv("VIP_CHAT_ID"))
ITEM_TITLE      = os.getenv("ITEM_TITLE", "VIP Pass")
ITEM_DESC       = os.getenv("ITEM_DESCRIPTION", "เข้ากลุ่มลับ")
ITEM_STARS      = int(os.getenv("ITEM_STARS", "100"))
INVITE_TTL_H    = int(os.getenv("INVITE_TTL_HOURS", "12"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"สวัสดี {update.effective_user.first_name or ''} 👋\n"
        f"แพ็กเกจ: {ITEM_TITLE}\nรายละเอียด: {ITEM_DESC}\n"
        f"ราคา: {ITEM_STARS} ⭐\n\nพิมพ์ /buy เพื่อชำระเงินด้วย Stars"
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = [LabeledPrice(label=ITEM_TITLE, amount=ITEM_STARS)]
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=ITEM_TITLE,
        description=ITEM_DESC,
        payload=f"vip-{update.effective_user.id}-{int(time.time())}",
        provider_token="",       # Stars ไม่ต้องใช้ provider_token
        currency="XTR",          # สกุลต้องเป็น XTR
        prices=prices,
    )

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sp: SuccessfulPayment = update.message.successful_payment
    user = update.effective_user
    charge_id = sp.telegram_payment_charge_id

    expire_ts = int((datetime.now(timezone.utc) + timedelta(hours=INVITE_TTL_H)).timestamp())
    invite = await context.bot.create_chat_invite_link(
        chat_id=VIP_CHAT_ID,
        name=f"VIP {user.id} {int(time.time())}",
        expire_date=expire_ts,
        member_limit=1
    )
    msg = ("จ่ายสำเร็จ ✅\n"
           f"Transaction: `{charge_id}`\n\n"
           f"ลิงก์เข้ากลุ่มลับ (ใช้ได้ครั้งเดียว): {invite.invite_link}\n"
           f"(ลิงก์หมดอายุใน {INVITE_TTL_H} ชม.)")
    await update.message.reply_markdown(msg)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, paid))
    app.run_polling()

if __name__ == "__main__":
    main()
