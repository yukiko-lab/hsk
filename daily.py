"""Отправляет «слово дня» или напоминание в Telegram.
Запускается по расписанию в GitHub Actions: python3 daily.py word | remind
"""
import datetime as dt
import json
import os
import random
import re
import sys
import urllib.parse
import urllib.request

TOKEN = os.environ["BOT_TOKEN"]
CHATS = [c.strip() for c in os.environ["CHAT_IDS"].split(",") if c.strip()]
APP_URL = os.environ["APP_URL"]


def send(chat, text):
    kb = {"inline_keyboard": [[{"text": "📖 Открыть карточки", "web_app": {"url": APP_URL}}]]}
    data = urllib.parse.urlencode({"chat_id": chat, "text": text, "reply_markup": json.dumps(kb)}).encode()
    urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=data, timeout=30)


def word_of_day():
    html = open("index.html", encoding="utf-8").read()
    w0 = re.search(r"const W0=`(.*?)`;", html, re.S).group(1)
    base = {}
    for line in w0.split("\n"):
        a = line.split("|")
        if len(a) >= 9:
            base[a[8] or a[1]] = {"lv": a[0], "h": a[1], "py": a[2], "ru": a[3], "ex": a[4], "ep": a[5], "er": a[6]}
    for line in open("ru.txt", encoding="utf-8"):
        if "=" not in line:
            continue
        wid, rest = line.rstrip("\n").split("=", 1)
        f = rest.split("|")
        if wid in base and len(f) >= 4:
            base[wid].update(ru=f[0], ex=f[1], ep=f[2], er=f[3])
    ready = [w for w in base.values() if w["ru"] and w["ex"]]
    return random.Random(dt.date.today().isoformat()).choice(ready)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "word"
    if mode == "word":
        w = word_of_day()
        text = f"📖 Слово дня (HSK {w['lv']})\n\n{w['h']}   {w['py']}\n{w['ru']}\n\n{w['ex']}\n{w['ep']}\n{w['er']}"
    else:
        text = "⏰ Пора повторить слова: десять минут сегодня, и серия не прервётся."
    for chat in CHATS:
        try:
            send(chat, text)
        except Exception as e:  # один недоступный чат не должен ломать остальные
            print("Ошибка отправки в чат", chat, e)


if __name__ == "__main__":
    main()
