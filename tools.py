from langchain_core.tools import tool
from typing import List, Annotated
from rag import FaissRagSource  # your existing classes
from bs4 import BeautifulSoup
# from langchain_community.tools import TavilySearchResults

# ——— Instantiate your RAG sources somewhere global ———
RAG_SOURCE = FaissRagSource("docs", "Официальная документация по электронному документообороту", "rag_sources/docs/vectors.index", "rag_sources/docs/texts.json")

@tool
def search_rag_tool(query: Annotated[str, "запрос для поиска"]) -> dict:
    """Выполнить поиск в документации по электронному документообороту"""
    resp: dict = RAG_SOURCE.query(query)
    return {"result": resp}

@tool
def question_user_tool(question: str) -> dict:
    """Задать пользователю вопрос"""
    # Print the question to the terminal
    print(f"\n[Follow-up question]: {question}")
    # Wait for the user's response
    answer = input("> ")
    return {"answer": answer}

@tool
def provide_answer_tool(answer: str) -> dict:
    """Предоставить полный и развернутый ответ"""
    return {"answer": answer}

@tool
def end_conversation_tool(farewell: str) -> dict:
    """Вежливо завершить диалог"""
    return {"farewell": farewell}

import requests

# ─── Read & Extract Webpage Text ───
@tool
def read_webpage_tool(url: Annotated[str, "URL страницы"]) -> dict:
    """Парсит страницу и возвращает только текст (без разметки)."""
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return {"text": text}

import datetime

# ─── Current Date ───
@tool
def current_date_tool() -> dict:
    """Возвращает текущую дату в формате ГГГГ-ММ-ДД."""
    return {"date": datetime.datetime.now().strftime("%Y-%m-%d")}

import math

# ─── Calculator ───
@tool
def calculator_tool(expression: Annotated[str, "Выражение для вычисления"]) -> dict:
    """Вычисляет математическое выражение и возвращает результат."""
    try:
        # безопасный eval с доступом только к math.*
        result = eval(expression, {"__builtins__": None}, math.__dict__)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def send_email_tool(
    recipient: Annotated[str, "email получателя"],
    subject: Annotated[str, "тема письма"],
    body: Annotated[str, "текст письма"],
) -> dict:
    """Отправляет email через SMTP Gmail."""
    user = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_PASSWORD")
    if not user or not password:
        return {"error": "GMAIL_USER or GMAIL_PASSWORD not set"}

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user, password)
            server.sendmail(user, [recipient], msg.as_string())
        return {"status": "sent"}
    except Exception as e:
        return {"error": str(e)}

import os
from langchain_tavily import TavilySearch
import smtplib
from email.mime.text import MIMEText

search_tool = TavilySearch(max_results=3)
search_tool.name = "search_tool"
