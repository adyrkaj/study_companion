import os
import json
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DATA_FILE = "user_data.json"

active_timers = {}


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                return {int(k): v for k, v in raw_data.items()}
        except Exception as e:
            print(f"⚠️ Failed to load JSON data: {e}")
    return {}


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Failed to save JSON data: {e}")


user_data = load_data()


def get_user_store(user_id: int):
    if user_id not in user_data:
        user_data[user_id] = {
            "lang": "en",
            "notes": [],
            "schedule": {day: None for day in DAYS_ORDER},
            "flashcards": [],
            "exams": [],
            "awaiting": None,
            "temp_data": {}
        }
        save_data()
    return user_data[user_id]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    store = get_user_store(user_id)
    store["awaiting"] = None

    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇦🇱 Shqip", callback_data="lang_sq")
        ]
    ]
    await update.message.reply_text(
        "👋 Welcome / Përshëndetje!\n\nPlease select a language / Zgjidhni gjuhën:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_main_menu(message_or_query, store):
    lang = store.get("lang", "en")
    if lang == "sq":
        msg = "📌 **Menyja Kryesore**\nZgjidhni një opsion më poshtë:"
        b_notes, b_sched, b_cards, b_timer, b_exams = "📝 Shënime", "📅 Orari", "🃏 Flashcards", "⏱️ Kohëmatësi i Studimit", "⏳ Provimet"
    else:
        msg = "📌 **Main Menu**\nSelect an option below:"
        b_notes, b_sched, b_cards, b_timer, b_exams = "📝 Notes", "📅 Schedule", "🃏 Flashcards", "⏱️ Study Timer", "⏳ Exams"

    keyboard = [
        [InlineKeyboardButton(b_notes, callback_data="menu_notes"),
         InlineKeyboardButton(b_sched, callback_data="menu_schedule")],
        [InlineKeyboardButton(b_cards, callback_data="menu_flashcards"),
         InlineKeyboardButton(b_exams, callback_data="menu_exams")],
        [InlineKeyboardButton(b_timer, callback_data="timer_start")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if hasattr(message_or_query, 'edit_message_text'):
        await message_or_query.edit_message_text(msg, reply_markup=markup, parse_mode="Markdown")
    else:
        await message_or_query.reply_text(msg, reply_markup=markup, parse_mode="Markdown")


async def run_study_timer(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE, lang: str):
    try:
        await asyncio.sleep(1500)

        break_msg = (
            "🔔 **Koha mbaroi!** Koha për një pushim 5 minutësh!"
            if lang == "sq"
            else "🔔 **Time's up!** Time for a 5-minute break!"
        )
        await context.bot.send_message(chat_id=chat_id, text=break_msg, parse_mode="Markdown")

        await asyncio.sleep(300)

        resume_msg = (
            "⚡ **Pushimi përfundoi!** Gati për raundin tjetër të studimit?"
            if lang == "sq"
            else "⚡ **Break finished!** Ready to start studying again?"
        )
        await context.bot.send_message(chat_id=chat_id, text=resume_msg, parse_mode="Markdown")

    except asyncio.CancelledError:
        pass
    finally:
        active_timers.pop(user_id, None)


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    store = get_user_store(user_id)
    await query.answer()

    data = query.data
    lang = store.get("lang", "en")

    if data.startswith("lang_"):
        store["lang"] = "en" if data == "lang_en" else "sq"
        save_data()
        await show_main_menu(query, store)

    elif data == "menu_main":
        store["awaiting"] = None
        save_data()
        await show_main_menu(query, store)

    elif data == "menu_notes":
        notes = store["notes"]
        if not notes:
            msg = "📝 Nuk keni asnjë shënim të ruajtur në sistem." if lang == "sq" else "📝 You have no saved notes in the system."
            keyboard = [[InlineKeyboardButton("➕ Shto Shënim" if lang == "sq" else "➕ Create New Note",
                                              callback_data="note_create")]]
        else:
            msg = f"📝 Keni {len(notes)} shënim(e) të ruajtura." if lang == "sq" else f"📝 You have {len(notes)} saved note(s)."
            keyboard = [
                [InlineKeyboardButton("➕ Shto Shënim" if lang == "sq" else "➕ Create New Note",
                                      callback_data="note_create")],
                [InlineKeyboardButton("📖 Lexo Shënimet" if lang == "sq" else "📖 Open Previous Note",
                                      callback_data="note_open_menu")],
                [InlineKeyboardButton("🗑️ Fshi Shënim" if lang == "sq" else "🗑️ Delete a Note",
                                      callback_data="note_delete_menu")]
            ]
        keyboard.append(
            [InlineKeyboardButton("🔙 Kthehu në Meny" if lang == "sq" else "🔙 Back to Menu", callback_data="menu_main")])
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "note_create":
        store["awaiting"] = "writing_note"
        save_data()
        msg = "✏️ Shkruani përmbajtjen e shënimit tuaj:" if lang == "sq" else "✏️ Please type out the content of your note and send it:"
        await query.edit_message_text(msg)

    elif data == "note_open_menu":
        keyboard = [[InlineKeyboardButton(f"📄 {n['name']}", callback_data=f"note_view_{i}")] for i, n in
                    enumerate(store["notes"])]
        keyboard.append([InlineKeyboardButton("🔙 Kthehu" if lang == "sq" else "🔙 Back", callback_data="menu_notes")])
        await query.edit_message_text(
            "Zgjidhni një shënim për ta lexuar:" if lang == "sq" else "Select a note to read:",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("note_view_"):
        idx = int(data.replace("note_view_", ""))
        note = store["notes"][idx]
        msg = f"📌 **{note['name']}**\n\n{note['text']}"
        back_btn = [InlineKeyboardButton("🔙 Kthehu" if lang == "sq" else "🔙 Back", callback_data="menu_notes")]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([back_btn]), parse_mode="Markdown")

    elif data == "note_delete_menu":
        keyboard = [[InlineKeyboardButton(f"🗑️ {n['name']}", callback_data=f"note_delete_{i}")] for i, n in
                    enumerate(store["notes"])]
        keyboard.append([InlineKeyboardButton("🔙 Kthehu" if lang == "sq" else "🔙 Back", callback_data="menu_notes")])
        await query.edit_message_text(
            "Zgjidhni shënimin që dëshironi të fshini:" if lang == "sq" else "Select a note to delete:",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("note_delete_"):
        idx = int(data.replace("note_delete_", ""))
        deleted_note = store["notes"].pop(idx)
        save_data()
        msg = f"✅ U fshi shënimi: **{deleted_note['name']}**" if lang == "sq" else f"✅ Deleted note: **{deleted_note['name']}**"
        await query.edit_message_text(msg, parse_mode="Markdown")
        await show_main_menu(query, store)

    elif data == "menu_schedule":
        sched = store["schedule"]
        has_schedule = any(v is not None for v in sched.values())
        if not has_schedule:
            msg = "📅 Nuk keni një orar të caktuar ende." if lang == "sq" else "📅 You don't have a schedule set up yet."
            keyboard = [[InlineKeyboardButton("➕ Krijo Orarin" if lang == "sq" else "➕ Create Schedule",
                                              callback_data="sched_input_Monday")]]
        else:
            msg = "📅 **Orari Im**\nDëshironi të shikoni orarin apo të bëni ndryshime?" if lang == "sq" else "📅 **Schedule**\nWould you like to view your schedule or make changes?"
            keyboard = [
                [InlineKeyboardButton("👁️ Shiko Orarin" if lang == "sq" else "👁️ See Schedule",
                                      callback_data="sched_see")],
                [InlineKeyboardButton("✏️ Ndrysho Orarin" if lang == "sq" else "✏️ Change Schedule",
                                      callback_data="sched_input_Monday")]
            ]
        keyboard.append(
            [InlineKeyboardButton("🔙 Kthehu në Meny" if lang == "sq" else "🔙 Back to Menu", callback_data="menu_main")])
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "sched_see":
        sched = store["schedule"]
        msg = "📅 **Orari Javor:**\n\n" if lang == "sq" else "📅 **Your Weekly Schedule:**\n\n"
        for day in DAYS_ORDER:
            empty_lbl = "— (Bosh)" if lang == "sq" else "— (Empty)"
            msg += f"• **{day}**: {sched[day] or empty_lbl}\n"
        back_btn = [InlineKeyboardButton("🔙 Kthehu" if lang == "sq" else "🔙 Back", callback_data="menu_schedule")]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([back_btn]), parse_mode="Markdown")

    elif data.startswith("sched_input_"):
        day = data.replace("sched_input_", "")
        store["awaiting"] = f"setting_sched_{day}"
        save_data()
        msg = f"📝 Shkruani orarin për **{day}**:" if lang == "sq" else f"📝 Please type the schedule for **{day}**:"
        keyboard = [
            [InlineKeyboardButton("⏭️ Kalot (Skip)" if lang == "sq" else "⏭️ Skip", callback_data=f"sched_skip_{day}")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("sched_skip_"):
        skipped_day = data.replace("sched_skip_", "")
        current_idx = DAYS_ORDER.index(skipped_day)
        if current_idx + 1 < len(DAYS_ORDER):
            next_day = DAYS_ORDER[current_idx + 1]
            store["awaiting"] = f"setting_sched_{next_day}"
            save_data()
            msg = f"📝 Shkruani orarin për **{next_day}**:" if lang == "sq" else f"📝 Please type the schedule for **{next_day}**:"
            keyboard = [[InlineKeyboardButton("⏭️ Kalot (Skip)" if lang == "sq" else "⏭️ Skip",
                                              callback_data=f"sched_skip_{next_day}")]]
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            store["awaiting"] = None
            save_data()
            done_msg = "✅ Konfigurimi i orarit u përfundua!" if lang == "sq" else "✅ Schedule setup complete!"
            await query.edit_message_text(done_msg)
            await show_main_menu(query, store)

    elif data == "menu_flashcards":
        cards = store["flashcards"]
        msg = f"🃏 **Flashcards ({len(cards)})**"
        keyboard = [
            [InlineKeyboardButton("➕ Shto Pyetje" if lang == "sq" else "➕ Add Card", callback_data="card_add_q")]]
        if cards:
            keyboard.append([InlineKeyboardButton("🎯 Fillo Kuisin" if lang == "sq" else "🎯 Start Quiz",
                                                  callback_data="card_quiz_0")])
        keyboard.append(
            [InlineKeyboardButton("🔙 Kthehu në Meny" if lang == "sq" else "🔙 Back to Menu", callback_data="menu_main")])
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "card_add_q":
        store["awaiting"] = "card_q"
        save_data()
        msg = "❓ Shkruani pyetjen për kartën e studimit:" if lang == "sq" else "❓ Type the question for the flashcard:"
        await query.edit_message_text(msg)

    elif data.startswith("card_quiz_"):
        idx = int(data.replace("card_quiz_", ""))
        cards = store["flashcards"]
        if idx < len(cards):
            card = cards[idx]
            store["awaiting"] = f"answering_quiz_{idx}"
            save_data()
            msg = (
                f"❓ **Pyetja {idx + 1}/{len(cards)}:**\n\n{card['q']}\n\n✍️ *Shkruani përgjigjen tuaj me tekst:* "
                if lang == "sq"
                else f"❓ **Question {idx + 1}/{len(cards)}:**\n\n{card['q']}\n\n✍️ *Type your answer below:* "
            )
            await query.edit_message_text(msg, parse_mode="Markdown")
        else:
            store["awaiting"] = None
            save_data()
            msg = "🎉 E përfundove kuisin!" if lang == "sq" else "🎉 Quiz completed!"
            back_btn = [InlineKeyboardButton("🔙 Kthehu" if lang == "sq" else "🔙 Back", callback_data="menu_flashcards")]
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([back_btn]))

    elif data == "menu_exams":
        exams = store["exams"]
        msg = "⏳ **Provimet / Detyrat:**\n\n" if lang == "sq" else "⏳ **Exams / Deadlines:**\n\n"
        if not exams:
            msg += "Nuk keni asnjë provim të regjistruar." if lang == "sq" else "No upcoming exams recorded."
        else:
            for ex in exams:
                unit = "ditë" if lang == "sq" else "days"
                status = "të mbetura!" if lang == "sq" else "left!"
                msg += f"• **{ex['name']}**: {ex['days']} {unit} {status}\n"

        keyboard = [
            [InlineKeyboardButton("➕ Shto Provim" if lang == "sq" else "➕ Add Exam", callback_data="exam_add")],
            [InlineKeyboardButton("🔙 Kthehu në Meny" if lang == "sq" else "🔙 Back to Menu", callback_data="menu_main")]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "exam_add":
        store["awaiting"] = "exam_name"
        save_data()
        msg = "📚 Shkruani emrin e lëndës/provimit:" if lang == "sq" else "📚 Type the subject/exam name:"
        await query.edit_message_text(msg)

    elif data == "timer_start":
        msg = (
            "⏱️ **Koha për të studiuar! (25 minuta)**\n*(Shkruani 'stop' për ta ndaluar kohëmatësin)*"
            if lang == "sq"
            else "⏱️ **Time to study! (25 minutes)**\n*(Write 'stop' to stop the timer)*"
        )
        await query.edit_message_text(msg, parse_mode="Markdown")

        if user_id in active_timers:
            active_timers[user_id].cancel()

        task = asyncio.create_task(run_study_timer(query.message.chat_id, user_id, context, lang))
        active_timers[user_id] = task


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    store = get_user_store(user_id)
    text = update.message.text.strip()
    awaiting = store["awaiting"]
    lang = store.get("lang", "en")

    if text.lower() == "stop":
        if user_id in active_timers:
            active_timers[user_id].cancel()
            active_timers.pop(user_id, None)
            stop_msg = "🛑 Kohëmatësi u ndalua!" if lang == "sq" else "🛑 Timer stopped!"
            await update.message.reply_text(stop_msg)
            await show_main_menu(update.message, store)
        else:
            no_timer_msg = "Nuk keni asnjë kohëmatës aktiv." if lang == "sq" else "You don't have an active timer running."
            await update.message.reply_text(no_timer_msg)
        return

    if awaiting and awaiting.startswith("answering_quiz_"):
        idx = int(awaiting.replace("answering_quiz_", ""))
        card = store["flashcards"][idx]
        correct_ans = card["a"].strip()

        if text.lower() == correct_ans.lower():
            res_msg = "🎯 **Saktë! ✅** Nuk keni bërë asnjë gabim." if lang == "sq" else "🎯 **Correct! ✅** Well done!"
        else:
            res_msg = (
                f"❌ **Gabim!**\n\nPërgjigja juaj: *{text}*\nPërgjigja e saktë: **{correct_ans}**"
                if lang == "sq"
                else f"❌ **Incorrect!**\n\nYour answer: *{text}*\nCorrect answer: **{correct_ans}**"
            )

        store["awaiting"] = None
        save_data()
        await update.message.reply_text(res_msg, parse_mode="Markdown")
        await show_main_menu(update.message, store)

    elif awaiting == "writing_note":
        store["temp_data"]["note_text"] = text
        store["awaiting"] = "naming_note"
        save_data()
        msg = "🏷️ Si dëshironi ta emërtoni këtë shënim?\n*(Shkruani një emër, ose dërgoni /skip për 'shënim pa emër')*" if lang == "sq" else "🏷️ What would you like to name this note?\n*(Type a name, or press /skip to call it 'unnamed note')*"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif awaiting == "naming_note":
        note_name = text if text != "/skip" else ("shënim pa emër" if lang == "sq" else "unnamed note")
        store["notes"].append({"name": note_name, "text": store["temp_data"]["note_text"]})
        store["awaiting"] = None
        save_data()
        msg = f"✅ Shënimi u ruajt si **{note_name}**!" if lang == "sq" else f"✅ Saved note as **{note_name}**!"
        await update.message.reply_text(msg, parse_mode="Markdown")
        await show_main_menu(update.message, store)

    elif awaiting and awaiting.startswith("setting_sched_"):
        current_day = awaiting.replace("setting_sched_", "")
        store["schedule"][current_day] = text
        current_idx = DAYS_ORDER.index(current_day)

        if current_idx + 1 < len(DAYS_ORDER):
            next_day = DAYS_ORDER[current_idx + 1]
            store["awaiting"] = f"setting_sched_{next_day}"
            save_data()
            msg = f"📝 Shkruani orarin për **{next_day}**:" if lang == "sq" else f"📝 Please type the schedule for **{next_day}**:"
            keyboard = [[InlineKeyboardButton("⏭️ Kalot (Skip)" if lang == "sq" else "⏭️ Skip",
                                              callback_data=f"sched_skip_{next_day}")]]
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            store["awaiting"] = None
            save_data()
            done_msg = "🎉 **Konfigurimi i orarit javor u përfundua!**" if lang == "sq" else "🎉 **Weekly schedule setup complete!**"
            await update.message.reply_text(done_msg, parse_mode="Markdown")
            await show_main_menu(update.message, store)

    elif awaiting == "card_q":
        store["temp_data"]["card_q"] = text
        store["awaiting"] = "card_a"
        save_data()
        msg = "💡 Shkruani përgjigjen e saktë:" if lang == "sq" else "💡 Type the correct answer:"
        await update.message.reply_text(msg)

    elif awaiting == "card_a":
        store["flashcards"].append({"q": store["temp_data"]["card_q"], "a": text})
        store["awaiting"] = None
        save_data()

        msg = "✅ Karta e studimit u shtua!" if lang == "sq" else "✅ Flashcard added!"
        keyboard = [
            [InlineKeyboardButton("➕ Shto një tjetër" if lang == "sq" else "➕ Add another",
                                  callback_data="card_add_q")],
            [InlineKeyboardButton("🎯 Fillo Kuisin" if lang == "sq" else "🎯 Start Quiz", callback_data="card_quiz_0")],
            [InlineKeyboardButton("🔙 Menyja Kryesore" if lang == "sq" else "🔙 Main Menu", callback_data="menu_main")]
        ]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif awaiting == "exam_name":
        store["temp_data"]["exam_name"] = text
        store["awaiting"] = "exam_days"
        save_data()
        msg = "🔢 Sa ditë kanë mbetur deri te provimi/detyra?" if lang == "sq" else "🔢 How many days left until the exam?"
        await update.message.reply_text(msg)

    elif awaiting == "exam_days":
        store["exams"].append({"name": store["temp_data"]["exam_name"], "days": text})
        store["awaiting"] = None
        save_data()
        msg = "✅ Provimi u regjistrua me sukses!" if lang == "sq" else "✅ Exam recorded successfully!"
        await update.message.reply_text(msg)
        await show_main_menu(update.message, store)

    else:
        await show_main_menu(update.message, store)


if __name__ == "__main__":
    print("🚀 Study Assistant Bot Running...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT, handle_text_input))

    app.run_polling()