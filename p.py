import os
import json
import asyncio
import aiohttp
import random
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USERS_FILE = "users.json"
BALANCE_FILE = "balance.json"
REDEEM_FILE = "redeem.json"

# Files for credential storage per category (as arrays)
FB_FILE = "fb.json"
G_FILE = "g.json"
T_FILE = "t.json"

# Payment config
UPI = "Paytm.s1dxrqc@pty"
MID = "SsklaO64982999248857"

# Admin ID
ADMIN_ID = 7479124922

# Conversation state for ADD BALANCE
ENTER_AMOUNT = 1

# ---------- Utility Functions for Users & Balances ----------
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_balances():
    if not os.path.exists(BALANCE_FILE):
        return {}
    with open(BALANCE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_balances(balances):
    with open(BALANCE_FILE, "w") as f:
        json.dump(balances, f)

# ---------- Utility Functions for Category Credential Files ----------
def load_fb():
    if not os.path.exists(FB_FILE):
        return []
    with open(FB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_fb(data):
    with open(FB_FILE, "w") as f:
        json.dump(data, f)

def load_google():
    if not os.path.exists(G_FILE):
        return []
    with open(G_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_google(data):
    with open(G_FILE, "w") as f:
        json.dump(data, f)

def load_twitter():
    if not os.path.exists(T_FILE):
        return []
    with open(T_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_twitter(data):
    with open(T_FILE, "w") as f:
        json.dump(data, f)

# ---------- Utility Functions for Redeem Codes ----------
def load_redeem():
    if not os.path.exists(REDEEM_FILE):
        return {}
    with open(REDEEM_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_redeem(data):
    with open(REDEEM_FILE, "w") as f:
        json.dump(data, f)

# ---------- Global Variables ----------
users_list = load_users()
balances = load_balances()

# ---------- Reply Keyboards (plain text) ----------
def get_main_menu():
    keyboard = [
        [KeyboardButton("📕 FACEBOOK ID"), KeyboardButton("🌐 GOOGLE ID")],
        [KeyboardButton("🐦 TWITTER ID"), KeyboardButton("💰 BALANCE")],
        [KeyboardButton("➕ ADD BALANCE"), KeyboardButton("☎️ CONTACT")],
        [KeyboardButton("📦 STOCK"), KeyboardButton("👤 OWNER")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_facebook_menu():
    keyboard = [
        [KeyboardButton("FB 1-BUY"), KeyboardButton("FB 2-BUY")],
        [KeyboardButton("FB 3-BUY"), KeyboardButton("FB 4-BUY")],
        [KeyboardButton("FB 5-BUY"), KeyboardButton("FB 6-BUY")],
        [KeyboardButton("FB 7-BUY"), KeyboardButton("FB 8-BUY")],
        [KeyboardButton("EXIT")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_google_menu():
    keyboard = [
        [KeyboardButton("G 1-BUY"), KeyboardButton("G 2-BUY")],
        [KeyboardButton("G 3-BUY"), KeyboardButton("G 4-BUY")],
        [KeyboardButton("G 5-BUY"), KeyboardButton("G 6-BUY")],
        [KeyboardButton("G 7-BUY"), KeyboardButton("G 8-BUY")],
        [KeyboardButton("EXIT")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_twitter_menu():
    keyboard = [
        [KeyboardButton("T 1-BUY"), KeyboardButton("T 2-BUY")],
        [KeyboardButton("T 3-BUY"), KeyboardButton("T 4-BUY")],
        [KeyboardButton("T 5-BUY"), KeyboardButton("T 6-BUY")],
        [KeyboardButton("T 7-BUY"), KeyboardButton("T 8-BUY")],
        [KeyboardButton("EXIT")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ---------- /start Handler ----------
async def start(update: Update, context) -> None:
    global users_list, balances
    user = update.effective_user
    if user.id not in users_list:
        users_list.append(user.id)
        save_users(users_list)
    user_key = str(user.id)
    if user_key not in balances:
        balances[user_key] = 0
        save_balances(balances)
    user_name = user.first_name if user.first_name else "there"
    image_url = "https://i.ibb.co/q3TFkx0V/IMG-20250315-125625.jpg"
    # Manually written small-caps reply text
    caption = ("❤️ ʜᴇʏ " + user_name + "!! ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ꜰꜰ ʙᴏᴛ!\n\n"
               "👉 ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ɴᴀᴠɪɢᴀᴛᴇ.\n\n"
               "❓ ɪꜰ ʏᴏᴜ ʜᴀᴠᴇ ǫᴜᴇꜱᴛɪᴏɴꜱ, ᴄᴏɴᴛᴀᴄᴛ @L1GENDFF.")
    await update.message.reply_photo(
        photo=image_url,
        caption=caption,
        reply_markup=get_main_menu(),
        reply_to_message_id=update.message.message_id
    )

# ---------- /users Handler ----------
async def users_command(update: Update, context) -> None:
    global users_list
    count = len(users_list)
    await update.message.reply_text(
        "✅ ᴜꜱᴇʀꜱ: " + str(count) + " ᴜꜱᴇʀꜱ.",
        reply_to_message_id=update.message.message_id
    )

# ---------- Handle Main Menu Button Presses ----------
async def handle_button_text(update: Update, context) -> None:
    text = update.message.text
    user = update.effective_user
    user_key = str(user.id)

    if text == "📕 FACEBOOK ID":
        await update.message.reply_text(
            "👉 ѕᴇʟᴇᴄᴛ ᴀ ꜰᴀᴄᴇʙᴏᴋ ɪᴅ ᴛᴏ ᴘᴜʀᴄʜᴀꜱᴇ:\n\nᴘʀɪᴄᴇ ᴘᴇʀ ɪᴅ: ₹30\nꜰᴏʀ ɪꜱꜱᴜᴇꜱ, ᴅᴍ @L1GENDFF",
            reply_markup=get_facebook_menu(),
            reply_to_message_id=update.message.message_id
        )
    elif text == "🌐 GOOGLE ID":
        await update.message.reply_text(
            "👉 ѕᴇʟᴇᴄᴛ ᴀ ɢᴏᴏɢʟᴇ ɪᴅ ᴛᴏ ᴘᴜʀᴄʜᴀꜱᴇ:\n\nᴘʀɪᴄᴇ ᴘᴇʀ ɪᴅ: ₹35\nꜰᴏʀ ɪꜱꜱᴜᴇꜱ, ᴅᴍ @L1GENDFF",
            reply_markup=get_google_menu(),
            reply_to_message_id=update.message.message_id
        )
    elif text == "🐦 TWITTER ID":
        await update.message.reply_text(
            "👉 ѕᴇʟᴇᴄᴛ ᴀ ᴛᴡɪᴛᴛᴇʀ ɪᴅ ᴛᴏ ᴘᴜʀᴄʜᴀꜱᴇ:\n\nᴘʀɪᴄᴇ ᴘᴇʀ ɪᴅ: ₹30\nꜰᴏʀ ɪꜱꜱᴜᴇꜱ, ᴅᴍ @L1GENDFF",
            reply_markup=get_twitter_menu(),
            reply_to_message_id=update.message.message_id
        )
    elif text == "💰 BALANCE":
        user_balance = balances.get(user_key, 0)
        await update.message.reply_text(
            "💰 ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ: ₹" + str(user_balance),
            reply_to_message_id=update.message.message_id
        )
    elif text == "➕ ADD BALANCE":
        await add_balance_start(update, context)
    elif text == "☎️ CONTACT":
        await update.message.reply_text(
            "☎️ ꜰᴏʀ ᴍᴀɴᴜᴀʟ ʙᴀʟᴀɴᴄᴇ ᴀᴅᴅɪᴛɪᴏɴ ᴀɴᴅ ɪᴅ ʟᴏɢɪɴ ᴀᴘᴘʀᴏᴠᴀʟ, ᴄᴏɴᴛᴀᴄᴛ @L1GENDFF",
            reply_to_message_id=update.message.message_id
        )
    elif text == "📦 STOCK":
        fb_stock = len(load_fb())
        g_stock = len(load_google())
        t_stock = len(load_twitter())
        message_text = ("► ᴀᴠᴀɪʟᴀʙʟᴇ ꜱᴛᴏᴄᴋ ◄\n\n"
                        "📄 ꜰᴀᴄᴇʙᴏᴋ ɪᴅꜱ      ► " + str(fb_stock) + "\n"
                        "📄 ɢᴏᴏɢʟᴇ ɪᴅꜱ        ► " + str(g_stock) + "\n"
                        "📄 ᴛᴡɪᴛᴛᴇʀ ɪᴅꜱ       ► " + str(t_stock))
        await update.message.reply_text(message_text, parse_mode="Markdown", reply_to_message_id=update.message.message_id)
    elif text == "👤 OWNER":
        inline_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("👉 VIEW OWNER'S INTRO", url="http://t.me/lvl8_seller_bot/Introlegend")
        ]])
        await update.message.reply_text(
            "👤 OWNER: @L1GENDFF",
            reply_markup=inline_keyboard,
            reply_to_message_id=update.message.message_id
        )
    elif text == "EXIT":
        await update.message.reply_text(
            "↩️ ʀᴇᴛᴜʀɴɪɴɢ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ...",
            reply_markup=get_main_menu(),
            reply_to_message_id=update.message.message_id
        )
    else:
        # --- Purchase flow handling ---
        if text.endswith("-BUY"):
            try:
                parts = text.split()
                category = parts[0]  # e.g., "FB", "G", "T"
                num_requested = int(parts[1].split("-")[0])
            except Exception:
                await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴘᴜʀᴄʜᴀꜱᴇ ғᴏʀᴍᴀᴛ.", reply_to_message_id=update.message.message_id)
                return

            if category.startswith("FB"):
                base_cost = 30
                category_code = "FB"
            elif category.startswith("G"):
                base_cost = 35
                category_code = "G"
            elif category.startswith("T"):
                base_cost = 30
                category_code = "T"
            else:
                await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴄᴀᴛᴇɢᴏʀʏ.", reply_to_message_id=update.message.message_id)
                return

            cost = base_cost * num_requested
            if balances.get(user_key, 0) < cost:
                await update.message.reply_text(
                    "❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ.\nꜱʟᴏᴛ ᴘʀɪᴄᴇ: ₹" + str(cost) + ", ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ: ₹" + str(balances.get(user_key, 0)) +
                    ".\nᴘʟᴇᴀꜱᴇ ᴀᴅᴅ ꜰᴜɴᴅꜱ ᴜꜱɪɴɢ ➕ ADD BALANCE.",
                    reply_to_message_id=update.message.message_id
                )
                return

            inline_keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ CONFIRM", callback_data=f"/ConfirmPurchase {category_code} {num_requested} {cost}"),
                InlineKeyboardButton("❌ CANCEL", callback_data="/CancelPurchase")
            ]])
            await update.message.reply_text(
                "❓ ᴄᴏɴꜰɪʀᴍ ᴘᴜʀᴄʜᴀꜱᴇ ᴏꜰ " + category_code + " " + str(num_requested) + "-BUY Ɥ ₹" + str(cost) +
                "?\nʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ: ₹" + str(balances.get(user_key, 0)),
                reply_markup=inline_keyboard,
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text("❌ ɪ'ᴍ ɴᴏᴛ ꜱᴜʀᴇ ᴡʜᴀᴛ ʏᴏᴜ ᴍᴇᴀɴ.", reply_to_message_id=update.message.message_id)

# ---------- Confirm / Cancel Purchase Callbacks ----------
async def confirm_purchase_callback(update: Update, context) -> None:
    global balances
    query = update.callback_query
    await query.answer()
    data = query.data.split()
    if len(data) < 4:
        await query.edit_message_text(text="❌ ɪɴᴠᴀʟɪᴅ ᴘᴜʀᴄʜᴀꜱᴇ ᴅᴀᴛᴀ.")
        return
    # Expected format: /ConfirmPurchase <category> <num_requested> <cost>
    _, category, num_str, cost_str = data
    try:
        num_requested = int(num_str)
        cost = float(cost_str)
    except ValueError:
        await query.edit_message_text(text="❌ ɪɴᴠᴀʟɪᴅ ᴘᴜʀᴄʜᴀꜱᴇ ᴅᴀᴛᴀ.")
        return

    user_id = query.message.chat.id
    user_key = str(user_id)

    if category == "FB":
        id_list = load_fb()
        base_cost = 30
        save_func = save_fb
    elif category == "G":
        id_list = load_google()
        base_cost = 35
        save_func = save_google
    elif category == "T":
        id_list = load_twitter()
        base_cost = 30
        save_func = save_twitter
    else:
        await query.edit_message_text(text="❌ ɪɴᴠᴀʟɪᴅ ᴄᴀᴛᴇɢᴏʀʏ.")
        return

    expected_cost = base_cost * num_requested
    if balances.get(user_key, 0) < expected_cost:
        await query.edit_message_text(text="❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ. ᴘʟᴇᴀꜱᴇ ᴀᴅᴅ ꜰᴜɴᴅꜱ ᴜꜱɪɴɢ ➕ ADD BALANCE.")
        return

    if len(id_list) < num_requested:
        await query.edit_message_text(text="❌ ɴᴏ ɪᴅꜱ ᴀᴠᴀɪʟᴀʙʟᴇ.")
        return

    purchased_creds = random.sample(id_list, num_requested)
    for cred in purchased_creds:
        id_list.remove(cred)

    balances[user_key] -= expected_cost
    save_balances(balances)
    save_func(id_list)

    message = "✅ ᴘᴜʀᴄʜᴀꜱᴇ ꜱᴜᴄᴄᴇꜱꜱғᴜʟ!\nʏᴏᴜʀ ᴄʀᴇᴅᴇɴᴛɪᴀʟ(ѕ):\n```\n"
    for idx, cred in enumerate(purchased_creds, start=1):
        message += f"ID {idx}: {cred.get('user')} : {cred.get('pass')}\n"
    message += "```"
    await query.edit_message_text(text=message, parse_mode="Markdown")

async def cancel_purchase_callback(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="❌ ᴘᴜʀᴄʜᴀꜱᴇ ᴄᴀɴᴄᴇʟᴇᴅ.")

# ---------- ADD BALANCE Conversation ----------
async def add_balance_start(update: Update, context) -> int:
    await update.message.reply_text(
        "💸 ᴇɴᴛᴇʀ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ ʏᴏᴜ Wɪꜱʜ ᴛᴏ ᴀᴅᴅ:",
        reply_to_message_id=update.message.message_id
    )
    return ENTER_AMOUNT

async def enter_amount(update: Update, context) -> int:
    global balances
    user = update.effective_user
    user_key = str(user.id)
    text = update.message.text
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError("Amount must be positive.")
    except ValueError:
        await update.message.reply_text(
            "❌ ᴘʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ, ᴘᴏꜱɪᴛɪᴠᴇ ᴀᴍᴏᴜɴᴛ.",
            reply_to_message_id=update.message.message_id
        )
        return ENTER_AMOUNT
    context.user_data["add_amount"] = amount
    await update.message.reply_text(
        "🔄 ɢᴇɴᴇʀᴀᴛɪɴɢ QR CODE...",
        reply_to_message_id=update.message.message_id
    )
    payment_url = f"https://paytms.aimbotaxe4.workers.dev/?id={MID}&upi={UPI}&amount={amount}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(payment_url) as resp:
                response = await resp.json()
        except Exception as e:
            await update.message.reply_text(
                f"❌ ᴇʀʀᴏʀ ɢᴇɴᴇʀᴀᴛɪɴɢ QR: {e}",
                reply_to_message_id=update.message.message_id
            )
            return ConversationHandler.END
    qr_image_url = response.get("qrImageUrl")
    track_id = response.get("trackId")
    if not qr_image_url or not track_id:
        await update.message.reply_text(
            "❌ ꜰᴀɪʟᴇᴅ TO ɢᴇɴᴇʀᴀᴛᴇ PAYMENT QR.",
            reply_to_message_id=update.message.message_id
        )
        return ConversationHandler.END
    inline_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ CHECK PAYMENT", callback_data=f"/CheckBalance {track_id} {amount}")
    ]])
    await update.message.reply_photo(
        photo=qr_image_url,
        caption=f"📌 ᴘᴀʏ ₹{amount}\n🆔 ᴏʀᴅᴇʀ ɪᴅ: `{track_id}`",
        reply_markup=inline_keyboard,
        reply_to_message_id=update.message.message_id
    )
    return ConversationHandler.END

async def cancel(update: Update, context) -> int:
    await update.message.reply_text(
        "❌ ᴀᴅᴅ ʙᴀʟᴀɴᴄᴇ ᴄᴀɴᴄᴇʟᴇᴅ.",
        reply_markup=get_main_menu(),
        reply_to_message_id=update.message.message_id
    )
    return ConversationHandler.END

# ---------- Check Payment Callback ----------
async def check_balance_callback(update: Update, context) -> None:
    global balances
    query = update.callback_query
    await query.answer()
    data = query.data.split()
    if len(data) < 3:
        await query.edit_message_caption(caption="❌ ɪɴᴠᴀʟɪᴅ ᴘᴀʏᴍᴇɴᴛ ᴅᴀᴛᴀ.")
        return
    track_id = data[1]
    try:
        amount = float(data[2])
    except ValueError:
        await query.edit_message_caption(caption="❌ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ ʀᴇᴄᴇɪᴠᴇᴅ.")
        return
    verify_url = f"https://thekinglearning.com/bot/Verify.php?id={MID}&trn={track_id}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(verify_url) as resp:
                response = await resp.json()
        except Exception as e:
            await query.edit_message_caption(caption=f"❌ ᴇʀʀᴏʀ ᴠᴇʀɪꜰʏɪɴɢ ᴘᴀʏᴍᴇɴᴛ: {e}")
            return
    status = response.get("STATUS", "")
    txn_amount_str = response.get("TXNAMOUNT", "0")
    try:
        txn_amount = float(txn_amount_str) if txn_amount_str.strip() != "" else 0
    except ValueError:
        txn_amount = 0
    if status == "TXN_SUCCESS" and abs(txn_amount - amount) < 0.01:
        user_id = query.message.chat.id
        user_key = str(user_id)
        balances[user_key] = balances.get(user_key, 0) + amount
        save_balances(balances)
        await query.edit_message_caption(
            caption=f"✅ ᴘᴀʏᴍᴇɴᴛ ꜱᴜᴄᴄᴇꜱꜱғᴜʟ!\n💰 ₹{amount} ʜᴀꜱ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ."
        )
    else:
        failed_img_url = "https://i.ibb.co/WtyD9CQ/4b13c916-4455-4c12-bd5d-b5492ed7039d.jpg"
        await query.edit_message_media(
            media=InputMediaPhoto(media=failed_img_url, caption="❌ ɴᴏ ᴘᴀʏᴍᴇɴᴛꜱ ʀᴇᴄᴇɪᴠᴇᴅ")
        )

# ---------- Admin Commands ----------
async def broadcast_command(update: Update, context) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.", reply_to_message_id=update.message.message_id)
        return
    args = context.args
    if not args:
        await update.message.reply_text("ᴜꜱᴀɢᴇ: /broadcast <message>", reply_to_message_id=update.message.message_id)
        return
    message_text = " ".join(args)
    count = 0
    for user_id in users_list:
        try:
            await context.bot.send_message(chat_id=user_id, text=message_text)
            count += 1
        except:
            pass
    await update.message.reply_text(f"🔊 ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴇɴᴛ ᴛᴏ {count} ᴜꜱᴇʀꜱ.", reply_to_message_id=update.message.message_id)

async def upload_command(update: Update, context) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.", reply_to_message_id=update.message.message_id)
        return
    args = context.args
    # Expected: /upload <category> user <user1> pass <pass1> [ user <user2> pass <pass2> ... ]
    if len(args) < 4:
        await update.message.reply_text("ᴜꜱᴀɢᴇ: /upload <category> user <user1> pass <pass1> [ user <user2> pass <pass2> ... ]", reply_to_message_id=update.message.message_id)
        return
    category = args[0].upper()
    credentials = []
    i = 1
    while i < len(args):
        if args[i].lower() == "user" and i+3 < len(args) and args[i+2].lower() == "pass":
            credentials.append({"user": args[i+1], "pass": args[i+3]})
            i += 4
        else:
            break
    if not credentials:
        await update.message.reply_text("❌ ɴᴏ ᴄʀᴇᴅᴇɴᴛɪᴀʟꜱ ᴘʀᴏᴠɪᴅᴇᴅ.", reply_to_message_id=update.message.message_id)
        return
    if category == "FB":
        save_fb(credentials)
        await update.message.reply_text(f"✅ ꜰᴀᴄᴇʙᴏᴋ ᴄʀᴇᴅᴇɴᴛɪᴀʟꜱ ᴜᴘᴅᴀᴛᴇᴅ ᴡɪᴛʜ {len(credentials)} ɪᴅꜱ.", reply_to_message_id=update.message.message_id)
    elif category == "G":
        save_google(credentials)
        await update.message.reply_text(f"✅ ɢᴏᴏɢʟᴇ ᴄʀᴇᴅᴇɴᴛɪᴀʟꜱ ᴜᴘᴅᴀᴛᴇᴅ ᴡɪᴛʜ {len(credentials)} ɪᴅꜱ.", reply_to_message_id=update.message.message_id)
    elif category == "T":
        save_twitter(credentials)
        await update.message.reply_text(f"✅ ᴛᴡɪᴛᴛᴇʀ ᴄʀᴇᴅᴇɴᴛɪᴀʟꜱ ᴜᴘᴅᴀᴛᴇᴅ ᴡɪᴛʜ {len(credentials)} ɪᴅꜱ.", reply_to_message_id=update.message.message_id)
    else:
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴄᴀᴛᴇɢᴏʀʏ. ᴜꜱᴇ FB, G, ᴏʀ T.", reply_to_message_id=update.message.message_id)

async def code_command(update: Update, context) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.", reply_to_message_id=update.message.message_id)
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("ᴜꜱᴀɢᴇ: /code <CODE> <limit> <amount>", reply_to_message_id=update.message.message_id)
        return
    code = args[0].upper()
    try:
        limit = int(args[1])
        amount = float(args[2])
    except ValueError:
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ʟɪᴍɪᴛ ᴏʀ ᴀᴍᴏᴜɴᴛ.", reply_to_message_id=update.message.message_id)
        return
    redeem_data = load_redeem()
    redeem_data[code] = {"limit": limit, "amount": amount}
    save_redeem(redeem_data)
    await update.message.reply_text(f"✅ ᴄᴏᴅᴇ {code} ᴄʀᴇᴀᴛᴇᴅ/ᴜᴘᴅᴀᴛᴇᴅ.\n• ʟɪᴍɪᴛ: {limit}\n• ᴀᴍᴏᴜɴᴛ: ₹{amount}", reply_to_message_id=update.message.message_id)

async def redeem_command(update: Update, context) -> None:
    user = update.effective_user
    user_key = str(user.id)
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("ᴜꜱᴀɢᴇ: /redeem <CODE>", reply_to_message_id=update.message.message_id)
        return
    code = args[0].upper()
    redeem_data = load_redeem()
    if code not in redeem_data:
        await update.message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ.", reply_to_message_id=update.message.message_id)
        return
    code_info = redeem_data[code]
    limit = code_info.get("limit", 0)
    amount = code_info.get("amount", 0)
    if limit <= 0:
        await update.message.reply_text("❌ ᴛʜɪꜱ ᴄᴏᴅᴇ ʜᴀꜱ ʙᴇᴇɴ ꜰᴜʟʟʏ ʀᴇᴅᴇᴍᴇᴅ.", reply_to_message_id=update.message.message_id)
        return
    user_balance = balances.get(user_key, 0)
    new_balance = user_balance + amount
    balances[user_key] = new_balance
    save_balances(balances)
    code_info["limit"] = limit - 1
    if code_info["limit"] <= 0:
        redeem_data.pop(code, None)
    else:
        redeem_data[code] = code_info
    save_redeem(redeem_data)
    await update.message.reply_text(f"✅ ᴄᴏᴅᴇ ʀᴇᴅᴇᴍᴇᴅ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ!\n💰 ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ ₹{amount}.\n🔖 ʏᴏᴜʀ ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: ₹{new_balance}", reply_to_message_id=update.message.message_id)

# ---------- Main ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("upload", upload_command))
    app.add_handler(CommandHandler("code", code_command))
    app.add_handler(CommandHandler("redeem", redeem_command))
    add_balance_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ ADD BALANCE$"), add_balance_start)],
        states={ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(add_balance_conv)
    app.add_handler(CallbackQueryHandler(confirm_purchase_callback, pattern=r"^/ConfirmPurchase"))
    app.add_handler(CallbackQueryHandler(cancel_purchase_callback, pattern=r"^/CancelPurchase"))
    app.add_handler(CallbackQueryHandler(check_balance_callback, pattern=r"^/CheckBalance"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_text))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()