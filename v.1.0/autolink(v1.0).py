import os
import re
import shutil
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
    "create_backup": False,
    "recursive": True,
    "stop_words": {"и", "в", "на", "с", "по", "к", "от"},
    "log_file": "autolink_log.txt",
    "dictionary_file": "СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT.md"  # файл словаря
}

# -----------------------------
# Настройка путей
# -----------------------------
NOTES_DIR = os.path.join(CONFIG["vault_dir"], CONFIG["notes_subfolder"])
VAULT_PATH = Path(CONFIG["vault_dir"])

# -----------------------------
# Словарь терминов
# -----------------------------
terms = {
    "break": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^break|break]]",
    "case": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^case|case]]",
    "catch": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^catch|catch]]",
    "class": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^class|class]]",
    "const": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^const|const]]",
    "continue": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^continue|continue]]",
    "debugger": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^debugger|debugger]]",
    "default": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^default|default]]",
    "delete": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^delete|delete]]",
    "do": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^do|do]]",
    "else": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^else|else]]",
    "enum": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^enum|enum]]",
    "export": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^export|export]]",
    "extends": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^extends|extends]]",
    "false": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^false|false]]",
    "finally": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^finally|finally]]",
    "for": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^for|for]]",
    "function": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^function|function]]",
    "if": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^if|if]]",
    "import": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^import|import]]",
    "in": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^in|in]]",
    "instanceof": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^instanceof|instanceof]]",
    "new": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^new|new]]",
    "null": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^null|null]]",
    "return": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^return|return]]",
    "super": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^super|super]]",
    "switch": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^switch|switch]]",
    "this": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^this|this]]",
    "throw": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^throw|throw]]",
    "true": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^true|true]]",
    "try": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^try|try]]",
    "typeof": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^typeof|typeof]]",
    "var": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^var|var]]",
    "void": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^void|void]]",
    "while": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^while|while]]",
    "with": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^with|with]]",
    "yield": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^yield|yield]]",
    "await": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^await|await]]",
    "implements": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^implements|implements]]",
    "interface": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^interface|interface]]",
    "let": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^let|let]]",
    "package": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^package|package]]",
    "private": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^private|private]]",
    "protected": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^protected|protected]]",
    "public": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^public|public]]",
    "static": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^static|static]]",
    "async": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^async|async]]",
    "of": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^of|of]]",
    "from": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^from|from]]",
    "as": "[[СЛОВАРЬ ТЕРМИНОВ JAVASCRIPT#^as|as]]"
}

# -----------------------------
# Регулярка для кодовых блоков и inline-кода
# -----------------------------
CODE_BLOCK_RE = re.compile(r"(```[\s\S]*?```|`.*?`)", re.MULTILINE)

# -----------------------------
# Логирование изменений
# -----------------------------
def log_change(log_lines):
    with open(os.path.join(CONFIG["vault_dir"], CONFIG["log_file"]), "a", encoding="utf-8") as log_f:
        for line in log_lines:
            log_f.write(line + "\n")

# -----------------------------
# Обработка текста
# -----------------------------
def replace_words(segment, note_names):
    # 1. Ссылки на словарь терминов
    pattern_terms = r"\b(" + "|".join(re.escape(term) for term in terms.keys()) + r")\b"

    def repl_terms(match):
        word = match.group(0)
        if re.search(r"\[\[.*?\b" + re.escape(word) + r"\b.*?\]\]", segment):
            return word
        return terms[word.lower()]

    segment = re.sub(pattern_terms, repl_terms, segment, flags=re.IGNORECASE)

    # 2. Ссылки на другие заметки
    for other_name in note_names:
        if other_name.lower() in segment.lower():
            pattern_note = rf"(?<!\[)\b{re.escape(other_name)}\b(?!\])"
            flags = 0 if CONFIG["case_sensitive"] else re.IGNORECASE
            segment = re.sub(pattern_note, f"[[{other_name}]]", segment, flags=flags)
    return segment

def link_terms(text, note_names):
    result = []
    last_index = 0
    for match in CODE_BLOCK_RE.finditer(text):
        segment = text[last_index:match.start()]
        segment = replace_words(segment, note_names)
        result.append(segment)
        result.append(match.group(0))  # кодовые блоки без изменений
        last_index = match.end()
    segment = text[last_index:]
    segment = replace_words(segment, note_names)
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
# Обход всех .md файлов
# -----------------------------
for note_name, filepath in notes.items():
    # Пропускаем сам файл словаря
    if os.path.basename(filepath).lower() == CONFIG["dictionary_file"].lower():
        continue

    log_lines = [f"Файл: {filepath}"]

    # Создаём резервную копию при необходимости
    if CONFIG["create_backup"]:
        backup_path = filepath + ".bak"
        shutil.copy2(filepath, backup_path)
        log_lines.append(f"  Создана резервная копия: {backup_path}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    original_text = text
    text = link_terms(text, note_names)

    if text != original_text:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        log_lines.append("  Ссылки обновлены")

    log_change(log_lines)

print(f"Автоссылки обновлены для всех заметок! Лог изменений в {CONFIG['log_file']}")
