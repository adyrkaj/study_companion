# 📚 Study Companion Telegram Bot

An interactive Telegram Bot designed to help students organize study schedules, manage notes, review flashcard quizzes, track exam countdowns, and run focus timers—with full bilingual support (English & Albanian).

## ✨ Features
* 📝 **Notes Manager:** Create, view, and delete study notes stored persistently in JSON.
* 📅 **Weekly Schedule:** Input and view day-by-day class timetables.
* 🃏 **Flashcards & Quiz Mode:** Add custom study questions and test knowledge with instant right/wrong grading.
* ⏳ **Exam Countdowns:** Track remaining days until upcoming exams or project deadlines.
* ⏱️ **Study Timer:** Run a 25-minute focus timer with break notifications and live cancellation (`stop`).
* 🌐 **Bilingual Support:** Seamless toggling between English and Albanian.

## Requirements
- Python 3.10 or newer (Python 3.11 is recommended).
- Telegram bot credentials for the `.env` file.

## 🚀 Setup & Run
1. Verify that Python 3.10 or newer is installed:
   ```bash
   # macOS/Linux
   python3 --version

   # Windows
   py --version
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/adyrkaj/study_companion.git
   cd study_companion
   ```

3. Create a virtual environment:
   ```bash
   # macOS/Linux
   python3 -m venv .venv

   # Windows
   py -3 -m venv .venv
   ```

4. Activate the virtual environment and install dependencies:
   ```bash
   # macOS/Linux
   source .venv/bin/activate

   # Windows PowerShell
   .venv\Scripts\Activate.ps1

   # Windows Command Prompt
   .venv\Scripts\activate.bat

   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

   When the environment is active, your shell prompt usually starts with
   `(.venv)`. Run `deactivate` when you are finished working in it.

5. Copy `.env.example` to `.env` and add your Telegram bot credentials.
6. Start the bot while the virtual environment is active:
   ```bash
   python main.py
   ```

## 💾 User data
The bot stores each user's notes, schedule, flashcards, and exams in `user_data.json`.
This file is created automatically when the bot runs and is excluded from Git.

`user_data.example.json` shows the expected structure using placeholder data. To
use it for local testing, copy it to `user_data.json` and replace `123456789`
with a Telegram user ID:

```bash
cp user_data.example.json user_data.json
```
