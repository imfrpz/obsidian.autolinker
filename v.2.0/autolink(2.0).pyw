import os
import re
from pathlib import Path

# -----------------------------
# Конфигурация
# -----------------------------
CONFIG = {
    "vault_dir": r"C:\Users\User\Documents\obsidian_gtd_vault-main\Obsidian",
    "notes_subfolder": "",        # если все заметки лежат прямо в vault, оставь "", иначе имя подпапки
    "ignore_short_words": True,
    "min_word_length": 3,
    "ignore_stop_words": True,
    "case_sensitive": False,
    "create_backup": False,       # резервные файлы не создаются
    "recursive": True,
    "stop_words": {"и", "в", "на", "с", "по", "к", "от"},
    "log_file": "autolink_log.txt",
    "dictionary_file": r"C:\Users\User\Documents\obsidian_gtd_vault-main\Obsidian\СИСТЕМА ЗНАНИЙ\1.ТЕХНИЧЕСКАЯ БАЗА\COMPUTER.CSIENCE++\JAVASCRIPT.learning\СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT.md"
}

# -----------------------------
# Настройка путей
# -----------------------------
NOTES_DIR = os.path.join(CONFIG["vault_dir"], CONFIG["notes_subfolder"])
VAULT_PATH = Path(CONFIG["vault_dir"])
DICTIONARY_PATH = CONFIG["dictionary_file"]

# -----------------------------
# Регулярка для кода и ссылок
# -----------------------------
CODE_OR_LINK_RE = re.compile(r"(```[\s\S]*?```|`.*?`|\[\[.*?\]\])", re.MULTILINE)

# -----------------------------
# Логирование изменений
# -----------------------------
def log_change(log_lines):
    with open(os.path.join(CONFIG["vault_dir"], CONFIG["log_file"]), "a", encoding="utf-8") as log_f:
        for line in log_lines:
            log_f.write(line + "\n")

# -----------------------------
# Загрузка терминов из словаря
# -----------------------------
def load_terms(dictionary_path):
    terms = {}
    with open(dictionary_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"######\s+(.*)", line)
            if match:
                term = match.group(1).strip()
                link = f"[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#{term}|{term}]]"
                terms[term] = link
    return terms

# -----------------------------
# Замена слов
# -----------------------------
def replace_words(segment, note_names, terms):
    # Ссылки на словарь терминов
    if terms:
        pattern_terms = r"\b(" + "|".join(re.escape(term) for term in terms.keys()) + r")\b"

        def repl_terms(match):
            word = match.group(0)
            # Игнорируем, если слово уже в [[…]]
            if re.search(r"\[\[.*?\b" + re.escape(word) + r"\b.*?\]\]", segment):
                return word
            return terms[word]
        segment = re.sub(pattern_terms, repl_terms, segment, flags=re.IGNORECASE)

    # Ссылки на другие заметки
    for other_name in note_names:
        if other_name.lower() in segment.lower():
            pattern_note = rf"(?<!\[)\b{re.escape(other_name)}\b(?!\])"
            flags = 0 if CONFIG["case_sensitive"] else re.IGNORECASE
            segment = re.sub(pattern_note, f"[[{other_name}]]", segment, flags=flags)
    return segment

# -----------------------------
# Обработка текста с учётом кода и ссылок
# -----------------------------
def link_terms(text, note_names, terms):
    result = []
    last_index = 0
    for match in CODE_OR_LINK_RE.finditer(text):
        segment = text[last_index:match.start()]
        segment = replace_words(segment, note_names, terms)
        result.append(segment)
        result.append(match.group(0))  # код и ссылки без изменений
        last_index = match.end()
    segment = text[last_index:]
    segment = replace_words(segment, note_names, terms)
    result.append(segment)
    return "".join(result)

# -----------------------------
# Получение списка всех заметок
# -----------------------------
notes = {}
for root, dirs, files in os.walk(NOTES_DIR):
    for file in files:
        if file.endswith(".md"):
            name = os.path.splitext(file)[0]
            notes[name] = os.path.join(root, file)
    if not CONFIG["recursive"]:
        break

note_names = list(notes.keys())

# -----------------------------
# Основной цикл обработки
# -----------------------------
terms = load_terms(DICTIONARY_PATH)

for note_name, filepath in notes.items():
    if os.path.basename(filepath).lower() == os.path.basename(DICTIONARY_PATH).lower():
        continue

    log_lines = [f"Файл: {filepath}"]

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    original_text = text
    text = link_terms(text, note_names, terms)

    if text != original_text:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        log_lines.append("  Ссылки обновлены")

    log_change(log_lines)

print(f"Автоссылки обновлены для всех заметок! Лог изменений в {CONFIG['log_file']}")
