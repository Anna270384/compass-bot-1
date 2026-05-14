import asyncio
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# States for the conversation
(
    START, RITUAL, EXPECTATION, DIARY_CREATED,
    STOP1_TASK1, STOP1_TASK2_THANKS, STOP1_TASK2_RELEASE,
    STOP2_TASK3, STOP2_TASK4_DEMONS, STOP2_TASK4_ANGELS,
    STOP3_TASK5, STOP3_TASK6,
    STOP4_TASK7, STOP4_TASK8,
    FINISH
) = range(15)

# Data storage
DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_file(user_id):
    return os.path.join(DATA_DIR, f"{user_id}.json")

def load_user_data(user_id):
    try:
        with open(get_user_file(user_id), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"entries": [], "current_stop": None}

def save_user_data(user_id, data):
    with open(get_user_file(user_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_pdf(user_id, user_name):
    """Generate a beautiful PDF diary for the user."""
    data = load_user_data(user_id)

    if not data["entries"]:
        return None

    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Register DejaVu font for Cyrillic support
    try:
        pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        font_name = 'DejaVu'
        font_bold = 'DejaVu-Bold'
    except Exception as e:
        # Fallback to Liberation Sans if DejaVu not found
        try:
            pdfmetrics.registerFont(TTFont('Liberation', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'))
            pdfmetrics.registerFont(TTFont('Liberation-Bold', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'))
            font_name = 'Liberation'
            font_bold = 'Liberation-Bold'
        except:
            # Last fallback
            font_name = 'Helvetica'
            font_bold = 'Helvetica-Bold'

    # Custom styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        textColor=colors.HexColor('#7F8C8D'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName=font_bold,
        fontSize=16,
        textColor=colors.HexColor('#E74C3C'),
        spaceAfter=12,
        spaceBefore=20,
        borderColor=colors.HexColor('#E74C3C'),
        borderWidth=1,
        borderPadding=5,
        leftIndent=0,
    )

    entry_title_style = ParagraphStyle(
        'EntryTitle',
        parent=styles['Heading3'],
        fontName=font_bold,
        fontSize=13,
        textColor=colors.HexColor('#2980B9'),
        spaceAfter=6,
        spaceBefore=15,
    )

    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        textColor=colors.HexColor('#95A5A6'),
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=10,
        leading=16,
        alignment=TA_JUSTIFY,
    )

    quote_style = ParagraphStyle(
        'QuoteStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        textColor=colors.HexColor('#8E44AD'),
        spaceAfter=15,
        leftIndent=20,
        rightIndent=20,
        leading=18,
        alignment=TA_CENTER,
        backColor=colors.HexColor('#F8F9FA'),
        borderPadding=10,
    )

    # Build PDF content
    story = []

    # Cover page
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("🧭", ParagraphStyle('Emoji', fontName=font_name, fontSize=48, alignment=TA_CENTER)))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Трансформационная игра", title_style))
    story.append(Paragraph('"Компас второй половины"', title_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Дневник путешественника", subtitle_style))
    story.append(Spacer(1, 1*cm))

    # User info
    story.append(Paragraph(f"<b>Путешественник:</b> {user_name}", subtitle_style))
    story.append(Paragraph(f"<b>Дата:</b> {datetime.now().strftime('%d.%m.%Y')}", subtitle_style))
    story.append(Spacer(1, 2*cm))

    # Quote
    story.append(Paragraph(
        '"От кризиса к возможностям.<br/>Карта вашего нового пути."',
        quote_style
    ))

    story.append(PageBreak())

    # Section: Preparation
    story.append(Paragraph("🌅 ПОДГОТОВКА К ПУТИ", section_style))

    # Section: Past
    story.append(Paragraph("🧳 ОСТАНОВКА 1: ПРОШЛОЕ", section_style))
    story.append(Paragraph('<i>"Багаж наследия"</i>', body_style))
    story.append(Spacer(1, 0.5*cm))

    # Section: Present
    story.append(Paragraph("⚓ ОСТАНОВКА 2: НАСТОЯЩЕЕ", section_style))
    story.append(Paragraph('<i>"Диагностика корабля"</i>', body_style))
    story.append(Spacer(1, 0.5*cm))

    # Section: Future
    story.append(Paragraph("🗺️ ОСТАНОВКА 3: БУДУЩЕЕ", section_style))
    story.append(Paragraph('<i>"Прорисовка карты"</i>', body_style))
    story.append(Spacer(1, 0.5*cm))

    # Section: Action
    story.append(Paragraph("🎯 ОСТАНОВКА 4: ДЕЙСТВИЕ", section_style))
    story.append(Paragraph('<i>"Первый шаг"</i>', body_style))
    story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # Entries
    story.append(Paragraph("📖 ЗАПИСИ ДНЕВНИКА", section_style))
    story.append(Spacer(1, 0.5*cm))

    for entry in data["entries"]:
        dt = datetime.fromisoformat(entry["timestamp"]).strftime("%d.%m.%Y %H:%M")

        story.append(Paragraph(f"{entry['title']}", entry_title_style))
        story.append(Paragraph(f"{dt}", date_style))

        # Clean content for PDF (replace newlines with <br/>)
        content = entry["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        content = content.replace("\n", "<br/>")
        content = content.replace("", "<br/>")

        story.append(Paragraph(content, body_style))
        story.append(Spacer(1, 0.3*cm))

    # Footer page
    story.append(PageBreak())
    story.append(Spacer(1, 5*cm))
    story.append(Paragraph(
        '"Я благодарен(на) себе за это время<br/>и открываю себя новым возможностям."',
        quote_style
    ))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(
        f"<b>Игра завершена:</b> {datetime.now().strftime('%d.%m.%Y')}",
        ParagraphStyle('Footer', fontName=font_name, fontSize=11, alignment=TA_CENTER, textColor=colors.HexColor('#7F8C8D'))
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


def add_entry(user_id, title, content):
    data = load_user_data(user_id)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "title": title,
        "content": content
    }
    data["entries"].append(entry)
    save_user_data(user_id, data)
    return entry

# Main menu keyboard
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Начать игру", callback_data="start_game")],
        [InlineKeyboardButton("📖 Мой дневник", callback_data="view_diary")],
        [InlineKeyboardButton("📄 Экспорт в PDF", callback_data="export_pdf")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")],
    ])

# Stop navigation keyboard
def stop_keyboard(current_stop):
    buttons = []
    stops = [
        ("🧳 Прошлое", "stop1"),
        ("⚓ Настоящее", "stop2"),
        ("🗺️ Будущее", "stop3"),
        ("🎯 Действие", "stop4"),
    ]
    for label, callback in stops:
        if callback == current_stop:
            label = f"▶️ {label}"
        buttons.append([InlineKeyboardButton(label, callback_data=callback)])
    buttons.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🧭 <b>Трансформационная игра "Компас второй половины"</b>

<i>От кризиса к возможностям. Карта вашего нового пути.</i>

Это инструмент для глубокого самоисследования. Здесь нет "правильных" ответов — есть только ваши честные.

<b>Важное правило:</b> Вы всегда главный в своей игре. Если вопрос вызывает сильный дискомфорт — пропустите его.

<b>Что вам понадобится:</b>
• Время: 2-3 часа без спешки
• Тетрадь или листы бумаги (для параллельной работы)
• Уютное место, где вас не побеспокоят

Готовы начать путешествие?
    """

    if update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text, 
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            welcome_text,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
    return ConversationHandler.END

# Help
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 <b>Как пользоваться ботом:</b>

1. Нажмите "🚀 Начать игру" для прохождения
2. Следуйте инструкциям поэтапно
3. Все ваши ответы сохраняются в личном дневнике
4. Можно проходить за несколько сессий

<b>Команды:</b>
/start — главное меню
/cancel — прервать текущее задание
/diary — посмотреть свой дневник

<b>Совет:</b> Играйте в спокойной обстановке, когда у вас есть время на размышления.
    """

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]))
    else:
        await update.message.reply_text(help_text, parse_mode="HTML")

# View diary
async def view_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_user_data(user_id)

    if not data["entries"]:
        text = "📖 <b>Ваш дневник пока пуст.</b>\n\nНачните игру, чтобы создать записи."
    else:
        text = "📖 <b>Мой дневник путешественника</b>\n\n"
        for i, entry in enumerate(data["entries"][-10:], 1):  # Show last 10
            dt = datetime.fromisoformat(entry["timestamp"]).strftime("%d.%m.%Y %H:%M")
            preview = entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
            text += f"<b>{i}. {entry['title']}</b> ({dt})\n{preview}\n\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

# ==================== GAME FLOW ====================

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = """
🎯 <b>Подготовка к игре</b>

<b>Ритуал начала (5 минут)</b>

1. Сядьте удобно, закройте глаза, сделайте 3 глубоких вдоха и выдоха.
2. Спросите себя: "Чего я жду от этой игры? Какой один вопрос мне бы хотелось прояснить?"
3. Не ищите ответ, просто задайте его своему подсознанию.

Когда будете готовы, напишите свой вопрос или ожидание от игры:
    """

    await query.edit_message_text(text, parse_mode="HTML")
    return RITUAL

async def ritual_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    expectation = update.message.text

    add_entry(user_id, "Ожидание от игры", expectation)

    text = f"""
✨ <b>Ваш вопрос записан:</b>\n<i>{expectation}</i>

Теперь создайте "Дневник Путешественника" — возьмите тетрадь, на первой странице напишите дату и заголовок: "Мой Компас. [Ваше имя]".

Это ваше личное пространство для инсайтов.

<b>Когда будете готовы, выберите первую остановку:</b>
    """

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=stop_keyboard("stop1"))
    return ConversationHandler.END

# ==================== STOP 1: PAST ====================

async def stop1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = """
🧳 <b>ОСТАНОВКА 1: ПРОШЛОЕ</b>
<i>"Багаж наследия"</i>

<b>Цель:</b> Разобрать свой "багаж" опыта, чтобы оставить ненужное и взять с собой ценное.

<b>Задание 1: "Карта достижений"</b>

Нарисуйте в тетради линию своей жизни от юности до сегодня. Отметьте:
• 5 ключевых вершин (успехи, победы)
• 3 важных долины (трудности, уроки)

Напишите рядом, какой навык или качество вы оттуда вынесли.

<i>Пример: "Долина: увольнение. Вынес: resilience, умение начинать с нуля"</i>

<b>Опишите здесь свои вершины и долины:</b>
    """

    await query.edit_message_text(text, parse_mode="HTML")
    return STOP1_TASK1

async def stop1_task1_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    content = update.message.text
    add_entry(user_id, "Карта достижений", content)

    text = """
✅ <b>Карта достижений сохранена!</b>

<b>Задание 2: "Благодарность и прощение"</b>

<b>Вопрос 1:</b> Кому и за что из вашего прошлого вы хотите сказать спасибо? (Даже если опыт был сложным)

Напишите свой ответ:
    """

    await update.message.reply_text(text, parse_mode="HTML")
    return STOP1_TASK2_THANKS

async def stop1_task2_thanks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    thanks = update.message.text
    add_entry(user_id, "Благодарность", thanks)

    text = """
✅ <b>Благодарность записана!</b>

<b>Вопрос 2:</b> Кого или что (может, себя самого) вам нужно отпустить, чтобы двигаться дальше легче?

Напишите это и мысленно скажите: "Я отпускаю тебя"
    """

    await update.message.reply_text(text, parse_mode="HTML")
    return STOP1_TASK2_RELEASE

async def stop1_task2_release(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    release = update.message.text
    add_entry(user_id, "Прощение", release)

    text = """
✅ <b>Ритуал прощения завершён.</b>

Остановка 1 пройдена! Вы разобрали свой багаж.

<b>Выберите следующую остановку:</b>
    """

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=stop_keyboard("stop2"))
    return ConversationHandler.END

# ==================== STOP 2: PRESENT ====================

async def stop2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = """
⚓ <b>ОСТАНОВКА 2: НАСТОЯЩЕЕ</b>
<i>"Диагностика корабля"</i>

<b>Цель:</b> Честно оценить, где вы находитесь прямо сейчас.

<b>Задание 3: "Колесо Баланса"</b>

Оцените каждую сферу от 1 (полный крах) до 10 (идеал):

1️⃣ Здоровье / Энергия
2️⃣ Карьера / Дело
3️⃣ Финансы
4️⃣ Отношения / Семья
5️⃣ Личностный рост
6️⃣ Творчество / Хобби
7️⃣ Отдых / Радость
8️⃣ Духовность / Смыслы

<b>Отправьте 8 чисел через запятую или с новой строки:</b>
<i>Пример: 7, 5, 6, 8, 4, 3, 5, 6</i>
    """

    await query.edit_message_text(text, parse_mode="HTML")
    return STOP2_TASK3

async def stop2_task3_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    scores_text = update.message.text

    # Parse scores
    try:
        scores = [int(x.strip()) for x in scores_text.replace(",", " ").split()]
        if len(scores) != 8:
            raise ValueError("Need exactly 8 scores")
        scores = [max(1, min(10, s)) for s in scores]  # Clamp to 1-10
    except:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте ровно 8 чисел от 1 до 10. Пример: 7, 5, 6, 8, 4, 3, 5, 6"
        )
        return STOP2_TASK3

    categories = [
        "Здоровье/Энергия", "Карьера/Дело", "Финансы", "Отношения/Семья",
        "Личностный рост", "Творчество/Хобби", "Отдых/Радость", "Духовность/Смыслы"
    ]

    wheel_text = "🎯 <b>Ваше Колесо Баланса:</b>\n\n"
    for cat, score in zip(categories, scores):
        bar = "█" * score + "░" * (10 - score)
        wheel_text += f"{cat}: {bar} {score}/10\n"

    avg = sum(scores) / len(scores)
    min_idx = scores.index(min(scores))
    max_idx = scores.index(max(scores))

    wheel_text += f"\n📊 Средний балл: {avg:.1f}/10\n"
    wheel_text += f"⚠️ Самая слабая сфера: {categories[min_idx]} ({scores[min_idx]}/10)\n"
    wheel_text += f"💪 Самая сильная сфера: {categories[max_idx]} ({scores[max_idx]}/10)\n"

    add_entry(user_id, "Колесо Баланса", wheel_text.replace("<b>", "").replace("</b>", ""))

    wheel_text += '\n<b>Задание 4: "Мои демоны и мои ангелы"</b>\n\n'
    wheel_text += "Напишите 3-5 главных страхов или убеждений, которые вас сдерживают ("Демоны"):\n"
    wheel_text += "<i>Примеры: "Уже поздно", "У меня не получится", "Что скажут люди?"</i>"

    await update.message.reply_text(wheel_text, parse_mode="HTML")
    return STOP2_TASK4_DEMONS

async def stop2_task4_demons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    demons = update.message.text
    add_entry(user_id, "Демоны (страхи)", demons)

    text = """
✅ <b>Демоны записаны.</b>

Теперь напишите 3-5 ваших суперсил, на которые вы можете опереться ("Ангелы"):

<i>Примеры: "Жизненный опыт", "Умение договариваться", "Любопытство", "Надежные друзья"</i>
    """

    await update.message.reply_text(text, parse_mode="HTML")
    return STOP2_TASK4_ANGELS

async def stop2_task4_angels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    angels = update.message.text
    add_entry(user_id, "Ангелы (ресурсы)", angels)

    text = """
✅ <b>Ангелы записаны!</b>

Остановка 2 пройдена! Вы провели диагностику своего "корабля".

<b>Выберите следующую остановку:</b>
    """

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=stop_keyboard("stop3"))
    return ConversationHandler.END

# ==================== STOP 3: FUTURE ====================

async def stop3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = """
🗺️ <b>ОСТАНОВКА 3: БУДУЩЕЕ</b>
<i>"Прорисовка карты"</i>

<b>Цель:</b> Помечтать и создать образ желаемого будущего, не ограничивая себя.

<b>Задание 5: "Идеальный день через 5 лет"</b>

Закройте глаза. Представьте обычный идеальный день вашей жизни через 5 лет. Вы просыпаетесь:

• <b>Где вы?</b> (Опишите место, дом, вид из окна)
• <b>Кто рядом с вами?</b>
• <b>Чем вы занимаетесь?</b> (Какая деятельность приносит радость и смысл?)
• <b>Какое у вас настроение?</b> (Покой? Азарт? Уверенность?)

<b>Опишите этот день во всех деталях:</b>
    """

    await query.edit_message_text(text, parse_mode="HTML")
    return STOP3_TASK5

async def stop3_task5_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    vision = update.message.text
    add_entry(user_id, "Идеальный день через 5 лет", vision)

    text = """
✅ <b>Видение будущего сохранено!</b>

<b>Задание 6: "Если бы не было страхов..."</b>

Какие 3 безумные, прекрасные или просто интересные вещи вы бы сделали в ближайшие год-два, если бы были абсолютно уверены в успехе?

<b>Напишите их:</b>
    """

    await update.message.reply_text(text, parse_mode="HTML")
    return STOP3_TASK6

async def stop3_task6_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dreams = update.message.text
    add_entry(user_id, "Безумные мечты", dreams)

    text = """
✅ <b>Мечты записаны!</b>

Остановка 3 пройдена! Вы нарисовали карту будущего.

<b>Выберите последнюю остановку:</b>
    """

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=stop_keyboard("stop4"))
    return ConversationHandler.END

# ==================== STOP 4: ACTION ====================

async def stop4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = """
🎯 <b>ОСТАНОВКА 4: ДЕЙСТВИЕ</b>
<i>"Первый шаг"</i>

<b>Цель:</b> Превратить инсайты в конкретный план действий.

<b>Задание 7: "Фокус на году"</b>

Основываясь на всех предыдущих заданиях, сформулируйте <b>одну главную цель</b> на ближайший год.

Это должен быть ваш личный фокус, а не "надо" извне.

<i>Примеры:
• "Начать учиться играть на саксофоне"
• "Сменить работу на более спокойную"
• "Восстановить энергию и здоровье"
• "Найти хобби, которое будет греть душу"</i>

<b>Ваша главная цель:</b>
    """

    await query.edit_message_text(text, parse_mode="HTML")
    return STOP4_TASK7

async def stop4_task7_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    goal = update.message.text
    add_entry(user_id, "Главная цель на год", goal)

    text = f"""
✅ <b>Цель записана:</b> <i>{goal}</i>

<b>Задание 8: "Первый километр пути"</b>

Большая цель пугает. Разбейте её на самый первый, <b>крошечный шаг</b>, который можно сделать уже завтра или на этой неделе.

<i>Примеры:
• Для цели "Найти хобби": "Завтра с 19:00 до 19:30 посмотреть на YouTube 3 видеоурока по гончарному делу"
• Для цели "Здоровье": "В среду записаться на прием к врачу для чек-апа"</i>

<b>Ваш первый шаг и дата:</b>
    """

    await update.message.reply_text(text, parse_mode="HTML")
    return STOP4_TASK8

async def stop4_task8_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    step = update.message.text
    add_entry(user_id, "Первый шаг", step)

    # Save the first step for the finish ritual
    context.user_data["first_step"] = step

    text = """
✅ <b>Первый шаг запланирован!</b>

<b>Переходим к завершению игры...</b>
    """

    await update.message.reply_text(text, parse_mode="HTML")

    # Trigger finish
    await finish_game(update, context)
    return ConversationHandler.END

# ==================== FINISH ====================

async def finish_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_step = context.user_data.get("first_step", "[ваш шаг из Задания 8]")

    # Get all entries for summary
    data = load_user_data(user_id)

    text = f"""
🎉 <b>ИГРА ЗАВЕРШЕНА!</b>

<b>Ритуал окончания</b>

Перечитайте свой дневник. Вспомните 1-3 самых главных инсайта.

<b>Напишите здесь свои главные инсайты:</b>
    """

    await update.message.reply_text(text, parse_mode="HTML")
    return FINISH

async def finish_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    insights = update.message.text
    add_entry(user_id, "Главные инсайты", insights)

    first_step = context.user_data.get("first_step", "")

    text = f"""
🧭 <b>Ваш Компас настроен!</b>

<b>Финальное обещание себе:</b>

"Я благодарен(на) себе за это время и открываю себя новым возможностям.

Мой первый шаг: {first_step}

Я делаю его до [укажите дату]"

<b>Сделайте глубокий вдох. Игра завершена. Дальше — путь. 🌟</b>

Все ваши ответы сохранены в дневнике. Вы можете вернуться к ним в любой момент через "📖 Мой дневник".
    """

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# ==================== CANCEL ====================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛑 Игра приостановлена. Ваш прогресс сохранён.\n\nВы можете продолжить с любой остановки через главное меню.",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

# ==================== MAIN ====================



# ==================== PDF EXPORT ====================

async def export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_name = update.effective_user.full_name or "Путешественник"

    # Check if diary has entries
    data = load_user_data(user_id)
    if not data["entries"]:
        await query.edit_message_text(
            "📄 <b>Экспорт в PDF</b>\n\n"
            "Ваш дневник пока пуст. Пройдите хотя бы одну остановку, чтобы создать PDF.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
        )
        return

    # Show loading message
    await query.edit_message_text(
        "📄 <b>Создаю ваш PDF-дневник...</b>\n\n"
        "Это займет несколько секунд.",
        parse_mode="HTML"
    )

    try:
        pdf_buffer = generate_pdf(user_id, user_name)
        if pdf_buffer:
            filename = f"Компас_второй_половины_{datetime.now().strftime('%Y%m%d')}.pdf"

            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=InputFile(pdf_buffer, filename=filename),
                caption=f"📖 Ваш дневник путешественника\n\n"
                        f"Всего записей: {len(data['entries'])}\n"
                        f"Дата создания: {datetime.now().strftime('%d.%m.%Y')}",
                parse_mode="HTML"
            )

            # Return to menu
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ <b>PDF успешно создан!</b>\n\nВаш дневник готов к печати или сохранению.",
                parse_mode="HTML",
                reply_markup=main_menu_keyboard()
            )
        else:
            await query.edit_message_text(
                "❌ Не удалось создать PDF. Попробуйте позже.",
                reply_markup=main_menu_keyboard()
            )
    except Exception as e:
        print(f"PDF generation error: {e}")
        await query.edit_message_text(
            "❌ Произошла ошибка при создании PDF. Убедитесь, что у бота есть записи в дневнике.",
            reply_markup=main_menu_keyboard()
        )


def main():
    # Get token from environment variable
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: Please set TELEGRAM_BOT_TOKEN environment variable")
        return

    application = Application.builder().token(token).build()

    # Conversation handler for the game flow
    game_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_game, pattern="^start_game$"),
        ],
        states={
            RITUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ritual_response)],
            STOP1_TASK1: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop1_task1_response)],
            STOP1_TASK2_THANKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop1_task2_thanks)],
            STOP1_TASK2_RELEASE: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop1_task2_release)],
            STOP2_TASK3: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop2_task3_response)],
            STOP2_TASK4_DEMONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop2_task4_demons)],
            STOP2_TASK4_ANGELS: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop2_task4_angels)],
            STOP3_TASK5: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop3_task5_response)],
            STOP3_TASK6: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop3_task6_response)],
            STOP4_TASK7: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop4_task7_response)],
            STOP4_TASK8: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop4_task8_response)],
            FINISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_response)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Stop navigation handlers (outside conversation)
    application.add_handler(CallbackQueryHandler(stop1, pattern="^stop1$"))
    application.add_handler(CallbackQueryHandler(stop2, pattern="^stop2$"))
    application.add_handler(CallbackQueryHandler(stop3, pattern="^stop3$"))
    application.add_handler(CallbackQueryHandler(stop4, pattern="^stop4$"))

    # Main menu handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("diary", view_diary))
    application.add_handler(CommandHandler("cancel", cancel))

    application.add_handler(CallbackQueryHandler(help_handler, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(view_diary, pattern="^view_diary$"))
    application.add_handler(CallbackQueryHandler(export_pdf, pattern="^export_pdf$"))
    application.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))

    application.add_handler(game_conv_handler)

    print("🤖 Bot started! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
