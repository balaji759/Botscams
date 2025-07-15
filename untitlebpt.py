import telebot
from telebot import types
import time
import threading

# --- Config ---
TOKEN = "8047147293:AAFs7k4EUTSdXIkeGAAPNIEY8Aq5jZW-MEc"
CHANNEL_ID = "@deskalert"
ADMIN_IDS = [6550284933, 7373470296]  # Add your admin chat IDs here
bot = telebot.TeleBot(TOKEN)

# Dictionary to store pending reports
pending_reports = {}

# --- Start Command ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_first_name = message.from_user.first_name or "User"
    greeting = (
        f"👋 Hey {user_first_name}, welcome to the *Scammer Expose Bot* 🔍\n\n"
        "🛡️ This bot is designed to help you *report scammers* and *expose frauds*,\n"
        "so others can stay safe and aware. 💡\n\n"
        "👇 Please choose an option below to get started:\n\n"
        "🧠 *BY* — [@z3x_b4n](https://t.me/z3x_b4n)\n"
        "💻 *Scripted by* — [@e_r_r_o_r_98](https://t.me/e_r_r_o_r_98) ⚙️🔥"
    )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("REPORT A SCAMMER")
    btn2 = types.KeyboardButton("REPORT IMP")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, greeting, reply_markup=markup, parse_mode="Markdown")

# --- Help Command ---
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📖 *How to Use Scammer Expose Bot* 🔍\n\n"
        "🚨 *REPORT A SCAMMER*\n"
        "➡️ Tap 'REPORT A SCAMMER' to start.\n"
        "➡️ Enter the scammer's username, amount, and proof link.\n\n"
        "⚠️ *REPORT IMP*\n"
        "➡️ Tap 'REPORT IMP' to begin.\n"
        "➡️ Provide the imposter's username and details.\n\n"
        "✅ Your report will be verified by admins before posting.\n\n"
        "🛠️ Facing any issue?"
    )

    contact_button = types.InlineKeyboardMarkup()
    contact_button.add(
        types.InlineKeyboardButton("📩 Contact Us Here", url="https://t.me/errorlive_bot")
    )

    bot.send_message(
        message.chat.id,
        help_text,
        reply_markup=contact_button,
        parse_mode="Markdown"
    )

# --- Loading Animation Function ---
def send_loading_message(chat_id):
    loading_messages = [
        "Processing your request...",
        "Verifying information...",
        "Finalizing report..."
    ]
    loading_message = bot.send_message(chat_id, loading_messages[0])
    for i in range(1, 4):
        time.sleep(1)
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=loading_message.message_id,
                text=loading_messages[i % len(loading_messages)]
            )
        except:
            pass

# --- Handle Reporting a Scammer ---
@bot.message_handler(func=lambda message: message.text == "REPORT A SCAMMER")
def report_scammer(message):
    bot.send_message(message.chat.id, "What is YOUR username? (e.g., @your_username)")
    bot.register_next_step_handler(message, process_reporter_username)

def process_reporter_username(message):
    reporter_username = message.text
    bot.send_message(message.chat.id, "What is the scammer's username? (e.g., @scammer_username)")
    bot.register_next_step_handler(message, process_username, reporter_username)

def process_username(message, reporter_username):
    username = message.text
    bot.send_message(message.chat.id, "How much money will be scammed?🛠️  (e.g., 100 ₹ , 100$)")
    bot.register_next_step_handler(message, process_amount, reporter_username, username)

def process_amount(message, reporter_username, username):
    amount = message.text
    bot.send_message(message.chat.id, "Please provide the proof channel URL (e.g., t.me/your_channel)")
    bot.register_next_step_handler(message, process_proof, reporter_username, username, amount)

def process_proof(message, reporter_username, username, amount):
    proof_url = message.text
    
    # Store the report data
    report_id = str(message.message_id) + str(message.chat.id)
    pending_reports[report_id] = {
        'reporter_username': reporter_username,
        'scammer_username': username,
        'amount': amount,
        'proof_url': proof_url,
        'reporter_chat_id': message.chat.id
    }
    
    # Create verification message for admins
    verification_message = (
        f"⚠️ NEW SCAMMER REPORT ⚠️\n\n"
        f"👤 Reporter: {reporter_username}\n"
        f"🦹 Scammer: {username}\n"
        f"💰 Amount: {amount}\n"
        f"🔗 Proof: {proof_url}\n\n"
        f"Report ID: {report_id}"
    )
    
    # Create approve/reject buttons
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{report_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{report_id}")
    )
    
    # Send to all admins
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, verification_message, reply_markup=markup)
        except Exception as e:
            print(f"Failed to send to admin {admin_id}: {e}")
    
    # Send confirmation to reporter
    bot.send_message(
        message.chat.id,
        "Thank you for reporting! Your report has been sent to admins for verification.",
        reply_markup=types.ReplyKeyboardRemove()
    )

# --- Handle Admin Callbacks ---
@bot.callback_query_handler(func=lambda call: True)
def handle_admin_callback(call):
    action, report_id = call.data.split('_')
    
    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "You are not authorized to perform this action.")
        return
    
    if report_id not in pending_reports:
        bot.answer_callback_query(call.id, "Report not found or already processed.")
        return
    
    report = pending_reports[report_id]
    
    if action == "approve":
        # Create channel message
        alert_message = (
            f"🚨⚠️𝗦𝗖𝗔𝗠𝗠𝗘𝗥 𝗔𝗟𝗘𝗥𝗧⚠️🚨\n\n"
            f"👤 𝗦𝗖𝗔𝗠𝗠𝗘𝗥 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘: {report['scammer_username']}\n"
            f"💰 𝗔𝗠𝗢𝗨𝗡𝗧: {report['amount']}\n\n"
            f"🕵️ 𝗥𝗘𝗣𝗢𝗥𝗧𝗘𝗗 𝗕𝗬: {report['reporter_username']}"
        )
        
        # Add proof button
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📎 View Proof", url=report['proof_url']))
        
        # Post to channel
        bot.send_message(CHANNEL_ID, alert_message, reply_markup=markup)
        
        # Notify reporter
        bot.send_message(
            report['reporter_chat_id'],
            "✅ Your report has been approved and posted to the channel!"
        )
        
        # Notify admins
        bot.answer_callback_query(call.id, "Report approved and posted to channel.")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ APPROVED REPORT ✅\n\n{call.message.text}",
            reply_markup=None
        )
    
    elif action == "reject":
        # Notify reporter
        bot.send_message(
            report['reporter_chat_id'],
            "❌ Your report was rejected by admins. Please provide more evidence if you believe this was a mistake."
        )
        
        # Notify admins
        bot.answer_callback_query(call.id, "Report rejected.")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"❌ REJECTED REPORT ❌\n\n{call.message.text}",
            reply_markup=None
        )
    
    # Remove from pending reports
    del pending_reports[report_id]

# --- Handle Reporting an Imposter ---
@bot.message_handler(func=lambda message: message.text == "REPORT IMP")
def report_imp(message):
    bot.send_message(message.chat.id, "What is the imposter's username? (e.g., @imposter_username)")
    bot.register_next_step_handler(message, process_imposter_username)

def process_imposter_username(message):
    username = message.text
    bot.send_message(message.chat.id, "Please provide details about the impersonation.")
    bot.register_next_step_handler(message, process_imposter_details, username)

def process_imposter_details(message, username):
    details = message.text
    alert_message = f"⚠️ Imposter Alert! ⚠️\n\nImposter Username: {username}\nDetails: {details}"
    
    # Start loading animation
    loading_thread = threading.Thread(target=send_loading_message, args=(message.chat.id,))
    loading_thread.start()
    
    # Send the alert to the channel
    bot.send_message(CHANNEL_ID, alert_message)
    
    # Wait for loading animation to finish
    loading_thread.join()
    
    bot.send_message(message.chat.id, "Thank you for reporting! The imposter alert has been sent to the channel.")

# --- Start Polling ---
if __name__ == '__main__':
    print("Bot is running...")
    bot.polling()