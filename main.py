# === CONFIG (แก้ตรงนี้) ==========================
BOT_TOKEN       = "8426669397:AAH-_sHmVq3uP3u-l79OxAFdtAr-nFOc138"
VIP_CHAT_ID     = -1002842045746    
ITEM_TITLE      = "VIP Lifetime Pass"
ITEM_DESC       = "เข้ากลุ่ม"
ITEM_STARS      = 100                
INVITE_TTL_H    = 2                
# ==================================================

import asyncio
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Final

from telegram import Update, LabeledPrice, SuccessfulPayment
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, PreCheckoutQueryHandler, filters,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("vip-bot")

# ---------- Commands ----------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        f"สวัสดี {update.effective_user.first_name or ''} 👋\n"
        f"แพ็กเกจ: {ITEM_TITLE}\n"
        f"รายละเอียด: {ITEM_DESC}\n"
        f"ราคา: {ITEM_STARS} ⭐\n\n"
        f"พิมพ์ /buy เพื่อชำระเงินด้วย Telegram Stars"
    )
    await update.message.reply_text(txt)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("คำสั่ง: /start /buy")

async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Stars ใช้ currency = XTR และ provider_token เว้นว่าง
    prices = [LabeledPrice(label=ITEM_TITLE, amount=ITEM_STARS)]
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=ITEM_TITLE,
        description=ITEM_DESC,
        payload=f"vip-{update.effective_user.id}-{int(time.time())}",
        provider_token="",
        currency="XTR",
        prices=prices,
    )

async def handle_precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ต้องตอบภายใน ~10วินาที ไม่งั้นการจ่ายจะล้มเหลว
    await update.pre_checkout_query.answer(ok=True)

async def handle_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sp: SuccessfulPayment = update.message.successful_payment
    user = update.effective_user

    # สร้างลิงก์เชิญแบบใช้ครั้งเดียว/หมดอายุ
    expire_ts = int((datetime.now(timezone.utc) + timedelta(hours=INVITE_TTL_H)).timestamp())
    invite = await context.bot.create_chat_invite_link(
        chat_id=VIP_CHAT_ID,
        name=f"VIP {user.id} {int(time.time())}",
        expire_date=expire_ts,
        member_limit=1,
    )

    msg = (
        "จ่ายสำเร็จ ✅\n"
        f"แพ็กเกจ: {ITEM_TITLE}\n"
        f"ลิงก์เข้ากลุ่ม (ใช้ได้ครั้งเดียว): {invite.invite_link}\n"
        f"ลิงก์หมดอายุใน {INVITE_TTL_H} ชม."
    )
    await update.message.reply_text(msg)

# ---------- Main ----------
def main() -> None:
    if not BOT_TOKEN or not isinstance(VIP_CHAT_ID, int):
        raise RuntimeError("ตั้งค่า BOT_TOKEN / VIP_CHAT_ID ให้ถูกก่อน")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("buy", cmd_buy))
    app.add_handler(PreCheckoutQueryHandler(handle_precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, handle_success))

    log.info("Bot starting…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
