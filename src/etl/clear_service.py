import re
import emoji

def remove_emoji(text):
    return emoji.replace_emoji(text, replace='')

    
# ----------------------------
# Очистка текста
# ----------------------------
def clean_text(text):
    if not text:
        return ""

    # удалить эмодзи
    text = remove_emoji(text)

    # нижний регистр
    text = text.lower()

    # убрать переносы строк
    text = re.sub(r'\n+', ' ', text)

    # убрать повторяющиеся символы (!!! → !)
    text = re.sub(r'([!?.,])\1+', r'\1', text)

    # убрать лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# ----------------------------
# Замена сущностей
# ----------------------------
def replace_entities(text):
    if not text:
        return ""

    # ссылки
    text = re.sub(r'http\S+', '[LINK]', text)

    # email
    text = re.sub(r'\S+@\S+', '[EMAIL]', text)

    # файлы (примерно)
    text = re.sub(r'\S+\.(pdf|docx|zip|png|jpg)', '[FILE]', text)

    return text


# ----------------------------
# Обработка одного сообщения
# ----------------------------
def process_message(msg):
    #извлекаем текст из поля
    text = msg.get("text", "")

    #проверка явл ли текст строко, если нет меняем на строку
    if not isinstance(text, str):
        text = str(text)

    #чистим текст
    text = replace_entities(text)
    text = clean_text(text)

    def valid_message(text):
        return bool(text.strip())
    
    #проверка не остался после чистки текст пустой
    if not valid_message(text):
        return None

    #наш результат
    return {
        "id": msg.get("id"),
        "date": msg.get("date"),
        "text": text
    }


# ----------------------------
# Обработка всего списка
# ----------------------------
def clear_data(messages):
    cleaned = []

    for msg in messages:
        processed = process_message(msg)
        if processed:
            cleaned.append(processed)

    return cleaned