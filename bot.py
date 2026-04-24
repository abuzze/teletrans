import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from config import TELEGRAM_BOT_TOKEN
from translator import translate_word
from sheets import save_word, get_all_words, get_word_count
from quiz import QuizSession

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Conversation states for quiz
QUIZ_ANSWER = 0

# Store pending translations and quiz sessions per user
pending_translations: dict[int, dict] = {}
quiz_sessions: dict[int, QuizSession] = {}


# --- Command Handlers ---

async def start(update: Update, context) -> None:
    await update.message.reply_text(
        "🇮🇹🇩🇪 Ciao! Ich bin dein Italienisch-Deutsch Vokabeltrainer.\n\n"
        "Schick mir ein Wort auf Italienisch oder Deutsch — ich übersetze es automatisch in die andere Sprache.\n\n"
        "Befehle:\n"
        "/quiz — Vokabelquiz starten\n"
        "/stats — Statistiken anzeigen"
    )


async def stats(update: Update, context) -> None:
    count = get_word_count()
    await update.message.reply_text(
        f"📊 Du hast bisher {count} Wörter gespeichert."
    )


# --- Translation Flow ---

async def handle_message(update: Update, context) -> None:
    user_id = update.effective_user.id

    # If user is in a quiz, treat this as a quiz answer
    if user_id in quiz_sessions:
        await handle_quiz_answer(update, context)
        return

    word = update.message.text.strip()
    if not word or len(word) > 200:
        await update.message.reply_text("Bitte schick mir ein einzelnes Wort oder eine kurze Phrase.")
        return

    await update.message.reply_text(f"⏳ Übersetze \"{word}\"...")

    result = translate_word(word)
    if result is None:
        await update.message.reply_text("❌ Übersetzung fehlgeschlagen. Bitte versuche es nochmal.")
        return

    # Store pending translation
    pending_translations[user_id] = result

    # Format response
    text = format_translation(result)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Speichern", callback_data="approve"),
            InlineKeyboardButton("❌ Verwerfen", callback_data="reject"),
        ]
    ])

    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


def format_translation(data: dict) -> str:
    richtung = data.get("richtung", "IT→DE")
    if richtung == "DE→IT":
        header = f"🇩🇪 <b>{data.get('deutsch', '')}</b>  →  🇮🇹 <b>{data.get('italiano', '')}</b>"
    else:
        header = f"🇮🇹 <b>{data.get('italiano', '')}</b>  →  🇩🇪 <b>{data.get('deutsch', '')}</b>"

    lines = [
        header,
        "",
        f"📂 Kategorie: {data.get('categoria', '')}",
    ]

    genere_it = data.get("genere_it", "-")
    genere_de = data.get("genere_de", "-")
    if genere_it != "-" or genere_de != "-":
        lines.append(f"⚥ Genus: {genere_it} / {genere_de}")

    plurale_it = data.get("plurale_it", "-")
    plurale_de = data.get("plurale_de", "-")
    if plurale_it != "-" or plurale_de != "-":
        lines.append(f"📝 Plural: {plurale_it} / {plurale_de}")

    lines.extend([
        "",
        f"💬 <i>{data.get('esempio_it', '')}</i>",
        f"💬 <i>{data.get('esempio_de', '')}</i>",
    ])

    return "\n".join(lines)


async def handle_callback(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data

    if action == "approve":
        data = pending_translations.pop(user_id, None)
        if data is None:
            await query.edit_message_text("⚠️ Keine ausstehende Übersetzung gefunden.")
            return

        success = save_word(data)
        if success:
            await query.edit_message_text(
                format_translation(data) + "\n\n✅ Gespeichert!",
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text("❌ Fehler beim Speichern. Bitte versuche es nochmal.")

    elif action == "reject":
        pending_translations.pop(user_id, None)
        await query.edit_message_text("❌ Verworfen.")


# --- Quiz Flow ---

async def start_quiz(update: Update, context) -> None:
    user_id = update.effective_user.id
    words = get_all_words()

    if len(words) < 3:
        await update.message.reply_text(
            "📚 Du brauchst mindestens 3 gespeicherte Wörter für ein Quiz.\n"
            f"Aktuell hast du {len(words)} Wörter."
        )
        return

    num_questions = min(5, len(words))
    session = QuizSession(words, num_questions)
    quiz_sessions[user_id] = session

    await send_quiz_question(update.message, session)


async def send_quiz_question(message, session: QuizSession) -> None:
    word = session.current_word
    if word is None:
        return

    q_num = session.current_index + 1
    total = session.total
    italiano = word.get("Italiano", "")

    await message.reply_text(
        f"❓ Frage {q_num}/{total}\n\n"
        f"Was heißt <b>{italiano}</b> auf Deutsch?",
        parse_mode="HTML",
    )


async def handle_quiz_answer(update: Update, context) -> None:
    user_id = update.effective_user.id
    session = quiz_sessions.get(user_id)

    if session is None or session.is_finished:
        quiz_sessions.pop(user_id, None)
        return

    answer = update.message.text.strip()
    correct, correct_answer = session.check_answer(answer)

    if correct:
        response = f"✅ Richtig!"
    else:
        response = f"❌ Falsch! Richtig wäre: <b>{correct_answer}</b>"

    if session.is_finished:
        response += "\n\n" + session.get_summary()
        quiz_sessions.pop(user_id, None)
        await update.message.reply_text(response, parse_mode="HTML")
    else:
        await update.message.reply_text(response, parse_mode="HTML")
        await send_quiz_question(update.message, session)


async def cancel_quiz(update: Update, context) -> None:
    user_id = update.effective_user.id
    if user_id in quiz_sessions:
        quiz_sessions.pop(user_id)
        await update.message.reply_text("Quiz abgebrochen.")


# --- Main ---

def main() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("quiz", start_quiz))
    app.add_handler(CommandHandler("cancel", cancel_quiz))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
