# Telegram Study Bot (`Study_companion`)

An automated study assistant Telegram bot built with Python. It helps students track notes, schedules, flashcards, upcoming exams, and Pomodoro study timers with isolated per-user JSON storage. It also supports Albanian & English based on the users choice!

---

## Prerequisites

Before starting, ensure you have the following installed on your machine:
* **Python 3.10+** (Check version with `python --version` or `python3 --version`)
* **Git**
* A valid **Telegram Bot Token** (Obtained from [@BotFather](https://t.me/BotFather) on Telegram)

---

## Project Structure

```text
Study_companion/
├── .github/
│   └── workflows/
│       └── test.yml          # GitHub Actions CI workflow script
├── tests/
│   ├── __init__.py           # Package marker
│   ├── conftest.py           # Shared test fixtures & temp path isolation
│   ├── test_persistence.py   # Storage load/save & corruption tests
│   └── test_bot_features.py  # Bot handler unit tests using mock Telegram objects
├── .env                      # Local environment secrets (ignored by Git)
├── .env.example              # Environment key template
├── user_data.json            # Local storage file (ignored by Git)
├── user_data.example.json    # Initial storage template
├── main.py                   # Bot startup entrypoint
├── requirements.txt          # Production runtime dependencies
├── requirements-dev.txt      # Development & testing dependencies
└── README.md                 # Project documentation
