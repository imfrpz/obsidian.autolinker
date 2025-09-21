import os
import re
from pathlib import Path

# -----------------------------
# Конфигурация
# -----------------------------
CONFIG = {
    "vault_dir": r"C:\Users\User\Documents\obsidian_gtd_vault-main\Obsidian",
    "notes_subfolder": "",
    "case_sensitive": False,
    "create_backup": False,
    "recursive": True,
    "log_file": "autolink_log.txt",
    "dictionaries_folder": r"C:\Users\User\Documents\obsidian_gtd_vault-main\Obsidian\СИСТЕМА ЗНАНИЙ\ПРОЕКТЫ\СЛОВАРИ ТЕРМИНОВ"
}

# -----------------------------
# Пути
# -----------------------------
NOTES_DIR = os.path.join(CONFIG["vault_dir"], CONFIG["notes_subfolder"])
DICTIONARIES_FOLDER = CONFIG["dictionaries_folder"]

# -----------------------------
# Игнорируем код и существующие ссылки
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
# Загрузка всех словарей из папки
# -----------------------------
def load_terms_from_folder(folder_path):
    terms = {}
    for file in os.listdir(folder_path):
        if file.lower().endswith(".md"):
            dict_path = os.path.join(folder_path, file)
            dict_name = os.path.splitext(file)[0]
            with open(dict_path, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.match(r"######\s+(.*)", line)
                    if match:
                        term = match.group(1).strip()
                        # ссылка формируется на название словаря + заголовок
                        link = f"[[{dict_name}#{term}|{term}]]"
                        terms[term.lower()] = link
    return terms

# -----------------------------
# Замена слов
# -----------------------------
def replace_words(segment, note_names, terms):
    if terms:
        pattern_terms = r"\b(" + "|".join(re.escape(term) for term in terms.keys()) + r")\b"

        def repl_terms(match):
            word = match.group(0)
            # игнорируем, если уже в [[…]]
            if re.search(r"\[\[.*?\b" + re.escape(word) + r"\b.*?\]\]", segment):
                return word
            # поиск по словарю без учета регистра
            term_key = next((k for k in terms if k.lower() == word.lower()), None)
            if term_key:
                return terms[term_key]
            return word

        segment = re.sub(pattern_terms, repl_terms, segment, flags=re.IGNORECASE)

    # ссылки на другие заметки
    for other_name in note_names:
        if other_name.lower() in segment.lower():
            pattern_note = rf"(?<!\[)\b{re.escape(other_name)}\b(?!\])"
            flags = 0 if CONFIG["case_sensitive"] else re.IGNORECASE
            segment = re.sub(pattern_note, f"[[{other_name}]]", segment, flags=flags)
    return segment

# -----------------------------
# Обработка текста
# -----------------------------
def link_terms(text, note_names, terms):
    result = []
    last_index = 0
    for match in CODE_OR_LINK_RE.finditer(text):
        segment = text[last_index:match.start()]
        segment = replace_words(segment, note_names, terms)
        result.append(segment)
        result.append(match.group(0))  # код и существующие ссылки без изменений
        last_index = match.end()
    segment = text[last_index:]
    segment = replace_words(segment, note_names, terms)
    result.append(segment)
    return "".join(result)

# -----------------------------
# Список всех заметок
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
terms = load_terms_from_folder(DICTIONARIES_FOLDER)

for note_name, filepath in notes.items():
    # пропускаем сами словари
    if Path(filepath).parent == Path(DICTIONARIES_FOLDER):
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
