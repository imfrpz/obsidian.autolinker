# Obsidian AutoLinker

**Automatic Linking Between Notes and Term Dictionaries in Obsidian**

## Project Description

This project provides a Python script for automatically generating internal links within Obsidian notes. The script analyzes note content and creates links to other notes and terms from dictionaries, while completely ignoring:

* code blocks and inline code (everything within `` ` ``),
* existing links (inside `[[…]]`),
* creating backup files to avoid cluttering the vault.

The project is ideal for managing large knowledge bases with numerous terms and interconnected notes.

## Features

* **Automatic links to term dictionaries**: supports one or multiple dictionaries.
* **Automatic links to other notes**: mentions of other notes are automatically linked to their actual files.
* **Ignore code and existing links**: nothing breaks inside code blocks or already existing links.
* **Multi-dictionary support**: multiple dictionaries can be stored in a folder and used simultaneously.
* **Change logging**: all changes are recorded in `autolink_log.txt` for tracking.
* **Full configuration via a config block**: allows specifying the Vault folder, note subfolders, stop words, case sensitivity, and recursive folder traversal.

## Installation and Usage

1. Clone the repository to any local folder:

   ```bash
   git clone https://github.com/<your-username>/obsidian-autolinker.git
   ```
2. Configure `CONFIG` in `autolink.py`, specifying the path to your Obsidian Vault and dictionary folder.
3. Run the script:

   ```bash
   python autolink.py
   ```
4. Check `autolink_log.txt` to review the changes made.

## Dictionary Structure

* Each dictionary is a Markdown file containing terminology.
* Each term must be formatted as an H6 heading (`###### Term`).
* The script automatically creates a link to the term in the format: `[[DICTIONARY#Term|Term]]`.
* Multiple dictionaries can be stored in the same folder; the script merges them when creating links.

## Usage Example

* If a note contains the word `function`, the script will create a link to the corresponding term in the dictionary.
* If a note mentions `Array`, a link `[[Array]]` is automatically created.
* Everything inside code blocks or existing links remains untouched.

## Advantages

* Fully automates linking in your knowledge base.
* Minimal risk of corrupting notes.
* Universal for different programming languages and topics.

⚠ Important Before First Run

Before using the script, make sure to create a backup of your Obsidian Vault.

Although the script is designed to:

* not touch code blocks or inline code,
* not modify existing links,
* not create unnecessary files,

unexpected situations may occur during the first run, especially if the note structure or term formatting differs from what is expected.

A backup ensures your data stays safe and allows you to restore it if necessary.

