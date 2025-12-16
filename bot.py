import json
import time
import random
import urllib.request
import urllib.parse
import ssl

TOKEN = "8462270023:AAF-I8eji50JsfKxOXUfd-fA0l0pOS7u194"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

SSL_CONTEXT = ssl._create_unverified_context()

def call_telegram(method: str, params: dict | None = None) -> dict:
    if params is None:
        params = {}

    data = urllib.parse.urlencode(params).encode("utf-8")
    url = BASE_URL + method

    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as response:
        resp_data = response.read().decode("utf-8")
        return json.loads(resp_data)


def send_message(
    chat_id: int,
    text: str,
    reply_markup: dict | None = None,
    parse_mode: str | None = None,
) -> dict:
    params: dict = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        params["parse_mode"] = parse_mode
    if reply_markup is not None:
        params["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    return call_telegram("sendMessage", params)


def edit_message(
    chat_id: int,
    message_id: int,
    text: str,
    reply_markup: dict | None = None,
    parse_mode: str | None = None,
) -> dict:
    params: dict = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
    }
    if parse_mode:
        params["parse_mode"] = parse_mode
    if reply_markup is not None:
        params["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    return call_telegram("editMessageText", params)


def answer_callback_query(callback_query_id: str) -> None:
    call_telegram("answerCallbackQuery", {"callback_query_id": callback_query_id})

QUIZ_QUESTIONS = [
    (
        "Что такое системная интеграция?",
        "Это объединение разнородных программных и аппаратных компонентов "
        "в единую согласованно работающую систему.",
    ),
    (
        "Что понимают под \"интерфейсом\" при системной интеграции?",
        "Набор правил и протоколов, по которым системы обмениваются данными.",
    ),
    (
        "Что такое API в контексте интеграции?",
        "Программный интерфейс, через который одна система может вызывать функции другой.",
    ),
    (
        "Для чего используются шины данных и очереди сообщений?",
        "Для обмена данными и событийным взаимодействием между сервисами.",
    ),
    (
        "Чем отличается монолитная система от интегрированной набором сервисов?",
        "Монолит — единое приложение, интегрированная система состоит из нескольких "
        "взаимодействующих модулей/сервисов.",
    ),
]

def main_menu_text() -> str:
    return (
        "<b>Привет! 👋</b>\n\n"
        "Я бот-ассистент по дисциплине «Системная интеграция».\n\n"
        "Через меня можно:\n"
        "• посмотреть требования к зачёту;\n"
        "• открыть чек-лист подготовки;\n"
        "• порешать теоретические вопросы;\n"
        "• посчитать примерную итоговую оценку.\n\n"
        "Выбери действие в меню ниже 👇"
    )


def build_main_menu() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "📚 О дисциплине", "callback_data": "about_subject"}],
            [{"text": "📅 Зачёт и требования", "callback_data": "schedule"}],
            [{"text": "✅ Чек-лист подготовки", "callback_data": "checklist"}],
            [{"text": "🎲 Вопрос по теме", "callback_data": "quiz"}],
            [{"text": "🧠 Мини-тест (1 вопрос)", "callback_data": "test_q1"}],
            [{"text": "🧮 Калькулятор оценки", "callback_data": "grade_help"}],
            [{"text": "ℹ️ О боте", "callback_data": "about_bot"}],
        ]
    }


def build_back_menu(extra_rows: list | None = None) -> dict:
    keyboard: list[list[dict]] = []
    if extra_rows:
        keyboard.extend(extra_rows)
    keyboard.append([{"text": "🔙 Главное меню", "callback_data": "back_to_menu"}])
    return {"inline_keyboard": keyboard}


def build_quiz_text() -> str:
    question, answer = random.choice(QUIZ_QUESTIONS)
    return (
        "<b>🎲 Вопрос по «Системной интеграции»</b>\n\n"
        f"<b>Вопрос:</b> {question}\n\n"
        f"<b>Ответ:</b> {answer}"
    )


def build_quiz_keyboard() -> dict:
    return build_back_menu(
        extra_rows=[[{"text": "🔁 Ещё вопрос", "callback_data": "quiz"}]]
    )

def handle_start(chat_id: int) -> None:
    send_message(
        chat_id,
        main_menu_text(),
        reply_markup=build_main_menu(),
        parse_mode="HTML",
    )


def handle_help(chat_id: int) -> None:
    text = (
        "<b>Справка по командам</b>\n\n"
        "/start — открыть главное меню\n"
        "/help — показать это сообщение\n"
        "/quiz — случайный теоретический вопрос\n"
        "/grade <лабы> <практики> <экзамен_0-100>\n\n"
        "Пример: <code>/grade 8 6 75</code>"
    )
    send_message(chat_id, text, parse_mode="HTML")


def handle_quiz(chat_id: int) -> None:
    send_message(
        chat_id,
        build_quiz_text(),
        reply_markup=build_quiz_keyboard(),
        parse_mode="HTML",
    )


def handle_grade(chat_id: int, text: str) -> None:
    parts = text.split()
    if len(parts) != 4:
        send_message(
            chat_id,
            "Формат: /grade <лабы> <практики> <экзамен_0-100>\n"
            "Например: /grade 8 6 75",
        )
        return

    try:
        labs = int(parts[1])
        practices = int(parts[2])
        exam = int(parts[3])
    except ValueError:
        send_message(
            chat_id,
            "Все три параметра должны быть числами.\n"
            "Пример: /grade 8 6 75",
        )
        return

    if not (0 <= exam <= 100):
        send_message(chat_id, "Балл за экзамен должен быть от 0 до 100.")
        return

    total = labs * 5 + practices * 3 + exam * 0.4

    if total >= 90:
        mark = "5 (отлично)"
    elif total >= 75:
        mark = "4 (хорошо)"
    elif total >= 60:
        mark = "3 (удовлетворительно)"
    else:
        mark = "2 (неудовлетворительно)"

    text_out = (
        "<b>📊 Расчёт примерной оценки</b>\n\n"
        f"<b>Лабораторные:</b> {labs}\n"
        f"<b>Практики:</b> {practices}\n"
        f"<b>Баллы за экзамен:</b> {exam}\n\n"
        f"<b>Суммарный балл:</b> {total:.1f}\n"
        f"<b>Ориентировочная оценка:</b> {mark}\n\n"
        "Формула условная, нужна для демонстрации логики в боте."
    )
    send_message(chat_id, text_out, parse_mode="HTML")


def handle_callback(callback_query: dict) -> None:
    callback_id = callback_query["id"]
    data = callback_query.get("data")
    message = callback_query.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    message_id = message.get("message_id")

    if chat_id is None or message_id is None:
        return

    answer_callback_query(callback_id)
    if data == "back_to_menu":
        edit_message(
            chat_id,
            message_id,
            main_menu_text(),
            reply_markup=build_main_menu(),
            parse_mode="HTML",
        )
        return

    if data == "schedule":
        text = (
            "<b>📅 Зачёт по дисциплине «Системная интеграция»</b>\n\n"
            "• Форма контроля: зачёт с оценкой.\n"
            "• Учитываются: лабораторные, практические задания и тестирование.\n"
            "• Важно понимать принципы интеграции, интерфейсы и примеры реальных решений.\n\n"
            "За точными критериями — к вашей кафедре и методичке, "
            "бот демонстрирует именно интеграцию с Telegram."
        )
        edit_message(
            chat_id,
            message_id,
            text,
            reply_markup=build_back_menu(),
            parse_mode="HTML",
        )

    elif data == "checklist":
        text = (
            "<b>✅ Чек-лист подготовки</b>\n\n"
            "1️⃣ Повтори термины: системная интеграция, интерфейс, API, протокол, шина данных.\n"
            "2️⃣ Пойми отличие монолита от набора интегрированных сервисов.\n"
            "3️⃣ Освежи примеры: Telegram-бот ↔ сервер, клиент ↔ БД, сервис ↔ сервис.\n"
            "4️⃣ Вспомни основные протоколы и форматы данных (HTTP, JSON и др.).\n"
            "5️⃣ Подготовь пример собственной интеграции — можно показать этого бота."
        )
        edit_message(
            chat_id,
            message_id,
            text,
            reply_markup=build_back_menu(),
            parse_mode="HTML",
        )

    elif data == "about_subject":
        text = (
            "<b>📚 О дисциплине «Системная интеграция»</b>\n\n"
            "Дисциплина изучает, как разные программные и аппаратные компоненты "
            "объединяются в единую систему.\n\n"
            "Ключевые идеи:\n"
            "• согласованное взаимодействие модулей;\n"
            "• интерфейсы и протоколы обмена данными;\n"
            "• интеграция уже существующих систем без полного переписывания;\n"
            "• надёжность и масштабируемость комплексных решений."
        )
        edit_message(
            chat_id,
            message_id,
            text,
            reply_markup=build_back_menu(),
            parse_mode="HTML",
        )

    elif data == "quiz":
        edit_message(
            chat_id,
            message_id,
            build_quiz_text(),
            reply_markup=build_quiz_keyboard(),
            parse_mode="HTML",
        )

    elif data == "grade_help":
        text = (
            "<b>🧮 Калькулятор оценки</b>\n\n"
            "Чтобы посчитать примерную итоговую оценку, используй команду:\n\n"
            "<code>/grade <лабы> <практики> <экзамен_0-100></code>\n\n"
            "Например:\n"
            "<code>/grade 8 6 75</code>\n\n"
            "Бот вычислит условный суммарный балл и подскажет ориентировочную оценку."
        )
        edit_message(
            chat_id,
            message_id,
            text,
            reply_markup=build_back_menu(),
            parse_mode="HTML",
        )

    elif data == "about_bot":
        text = (
            "<b>ℹ️ О боте</b>\n\n"
            "Этот бот создан как практический пример по дисциплине «Системная интеграция».\n\n"
            "Он демонстрирует:\n"
            "• интеграцию Telegram с Python-приложением через HTTP Bot API;\n"
            "• обработку команд и нажатий на inline-кнопки;\n"
            "• простую предметную логику (подготовка к зачёту, мини-тест, калькулятор оценки).\n\n"
            "Исходный код бота хранится в репозитории GitHub, который можно показать преподавателю."
        )
        edit_message(
            chat_id,
            message_id,
            text,
            reply_markup=build_back_menu(),
            parse_mode="HTML",
        )

    elif data == "test_q1":
        text = (
            "<b>🧠 Мини-тест</b>\n\n"
            "<b>Вопрос:</b> Что в контексте интеграции лучше всего описывает термин «API»?\n\n"
            "Выбери один вариант ответа:"
        )
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "A) База данных для хранения логов",
                        "callback_data": "test1_A",
                    }
                ],
                [
                    {
                        "text": "B) Программный интерфейс для вызова функций системы",
                        "callback_data": "test1_B",
                    }
                ],
                [
                    {
                        "text": "C) Графический интерфейс приложения",
                        "callback_data": "test1_C",
                    }
                ],
                [{"text": "🔙 Главное меню", "callback_data": "back_to_menu"}],
            ]
        }
        edit_message(
            chat_id,
            message_id,
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    elif data and data.startswith("test1_"):
        choice = data.split("_", 1)[1]
        correct = "B"

        if choice == correct:
            result_text = (
                "✅ Верно! API — это программный интерфейс для взаимодействия систем."
            )
        else:
            result_text = (
                "❌ Неверно.\n\n"
                "Правильный ответ: B) Программный интерфейс для вызова функций системы."
            )

        text = (
            "<b>🧠 Мини-тест — результат</b>\n\n"
            f"{result_text}\n\n"
            "Можешь вернуться в главное меню или пройти вопрос ещё раз."
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔁 Пройти снова", "callback_data": "test_q1"}],
                [{"text": "🔙 Главное меню", "callback_data": "back_to_menu"}],
            ]
        }
        edit_message(
            chat_id,
            message_id,
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    else:
        edit_message(
            chat_id,
            message_id,
            "Неизвестный пункт меню. Напиши /start, чтобы открыть главное меню.",
            reply_markup=build_main_menu(),
            parse_mode="HTML",
        )

def handle_message(message: dict) -> None:
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if chat_id is None:
        return

    text = message.get("text") or ""

    if text.startswith("/start"):
        handle_start(chat_id)
    elif text.startswith("/help"):
        handle_help(chat_id)
    elif text.startswith("/quiz"):
        handle_quiz(chat_id)
    elif text.startswith("/grade"):
        handle_grade(chat_id, text)
    else:
        send_message(
            chat_id,
            "Я бот по дисциплине «Системная интеграция».\n"
            "Напиши /start, чтобы открыть главное меню.",
        )


def main() -> None:
    offset = None
    print("Бот запущен. Ожидаю обновления...")

    while True:
        try:
            params: dict = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset

            updates = call_telegram("getUpdates", params)

            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                if "message" in update:
                    handle_message(update["message"])
                elif "callback_query" in update:
                    handle_callback(update["callback_query"])

        except Exception as e:
            print("Ошибка в основном цикле:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()