import telebot
import json
import os

BOT_TOKEN = "8383810011:AAGYZo17APTOCIbBzMERZjkQ7vIfgeCxv7Y"
ADMIN_ID = 7606197696  # thay bằng telegram id của bạn
TOKEN_FILE = "token_vn.json"

bot = telebot.TeleBot(BOT_TOKEN)


# Hàm load token từ file
def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


# Hàm lưu token ra file
def save_tokens(tokens):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2, ensure_ascii=False)


# Lệnh start
@bot.message_handler(commands=["start"])
def start(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "Chào admin 👋\nDùng /help để xem danh sách lệnh.")


# Lệnh help
@bot.message_handler(commands=["help"])
def help_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(
        message,
        "📌 Các lệnh quản lý token:\n\n"
        "/listtokens - Xem danh sách token\n"
        "/addtoken uid|token - Thêm token\n"
        "/deltoken uid - Xóa token theo UID\n\n"
        "👉 Bạn cũng có thể gửi file *token_vn.json* để update trực tiếp.",
    )


# Lệnh list tokens
@bot.message_handler(commands=["listtokens"])
def list_tokens(message):
    if message.from_user.id != ADMIN_ID:
        return
    tokens = load_tokens()
    if not tokens:
        bot.reply_to(message, "❌ Chưa có token nào trong file.")
        return
    msg = "📑 Danh sách token:\n"
    for t in tokens:
        msg += f"- UID: `{t['uid']}`\n"
    bot.reply_to(message, msg, parse_mode="Markdown")


# Lệnh add token
@bot.message_handler(commands=["addtoken"])
def add_token(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, data = message.text.split(" ", 1)
        uid, token = data.split("|", 1)
    except:
        bot.reply_to(message, "❌ Sai cú pháp.\nVí dụ: /addtoken 12345|abcxyz")
        return

    tokens = load_tokens()
    # Kiểm tra nếu uid đã tồn tại thì update
    for t in tokens:
        if t["uid"] == uid:
            t["token"] = token
            save_tokens(tokens)
            bot.reply_to(message, f"✅ Token UID {uid} đã được cập nhật.")
            return

    # Nếu chưa có thì thêm mới
    tokens.append({"uid": uid, "token": token})
    save_tokens(tokens)
    bot.reply_to(message, f"✅ Đã thêm token UID {uid}.")


# Lệnh delete token
@bot.message_handler(commands=["deltoken"])
def delete_token(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split(" ", 1)
    except:
        bot.reply_to(message, "❌ Sai cú pháp.\nVí dụ: /deltoken 12345")
        return

    tokens = load_tokens()
    new_tokens = [t for t in tokens if t["uid"] != uid]

    if len(tokens) == len(new_tokens):
        bot.reply_to(message, f"⚠️ Không tìm thấy UID {uid}.")
    else:
        save_tokens(new_tokens)
        bot.reply_to(message, f"🗑️ Đã xóa token UID {uid}.")


# Nhận file token_vn.json và update
@bot.message_handler(content_types=["document"])
def handle_file(message):
    if message.from_user.id != ADMIN_ID:
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    if message.document.file_name != TOKEN_FILE:
        bot.reply_to(
            message,
            "❌ Tên file không hợp lệ. Vui lòng gửi đúng file `token_vn.json`.",
        )
        return

    with open(TOKEN_FILE, "wb") as f:
        f.write(downloaded_file)

    bot.reply_to(message, "✅ File token_vn.json đã được cập nhật thành công.")


print("🤖 Bot đang chạy...")
bot.infinity_polling()