# Deployed by:
# uvicorn app:app --reload --host 0.0.0.0 --port 5678
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Union

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from common import LoggingMiddleware, get_logger

HERE = Path(__file__).parent
log_file_path = HERE / "app.log"
logger = get_logger(__file__, log_file_path)

questions_file_path = HERE / "questions.json"
pin_file_path = HERE / "correct_pin.txt"
words_zubenka_file_path = HERE / "words_zubenka.txt"
words_ajtak_file_path = HERE / "words_ajtak.txt"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(LoggingMiddleware, log=logger.info)

templates = Jinja2Templates(directory="templates", trim_blocks=True, lstrip_blocks=True)


def get_questions() -> List[dict]:
    with open(questions_file_path, "r") as f:
        return json.load(f)


def get_pin() -> str:
    with open(pin_file_path, "r") as f:
        return f.read().strip()


def get_hidden_words_zubenka() -> str:
    with open(words_zubenka_file_path, "r") as f:
        return f.read().strip()


def get_hidden_words_ajtak() -> str:
    with open(words_ajtak_file_path, "r") as f:
        return f.read().strip()


class QuizAnswer(BaseModel):
    question_id: str
    answer: Union[str, List[str]]  # This allows for single or multiple answers


class QuizData(BaseModel):
    answers: List[QuizAnswer]


@app.get("/")
async def base(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


@app.get("/quiz/ajtak/")
async def level_0_get_for_everything(request: Request):
    pin = request.query_params.get("pin", None)
    logger.info(f"GET level0 pin: {pin}")

    if pin == get_pin():
        return templates.TemplateResponse(
            "quiz_ajtak.html",
            {
                "request": request,
                "method": "get",
                "level": 0,
                "token": None,
                "invalid_pin": False,
                "hidden_message": get_hidden_words_ajtak(),
            },
        )
    else:
        return templates.TemplateResponse(
            "quiz_ajtak.html",
            {
                "request": request,
                "method": "get",
                "level": 0,
                "token": None,
                "invalid_pin": pin is not None,
                "hidden_message": None,
            },
        )


@app.get("/quiz/zubenka/")
async def quiz_zubenka(request: Request):
    return templates.TemplateResponse(
        "quiz_zubenka.html",
        {"request": request},
    )


@app.get("/quiz/zubenka/questions")
async def questions(request: Request):
    # make sure to delete answer from questions
    questions = get_questions()
    for question in questions:
        if "answer" in question:
            del question["answer"]
    return {"questions": questions}


@app.post("/quiz/zubenka/submit_quiz")
async def submit_quiz(quiz_data: QuizData):
    logger.info(quiz_data)
    questions = get_questions()

    if not len(quiz_data.answers) == len(questions):
        return {"message": "Špatně!", "is_correct": False, "extra_data": ""}

    is_correct = True
    for answer in quiz_data.answers:
        connected_question = next(
            (
                question
                for question in questions
                if question["id"] == answer.question_id
            ),
            None,
        )
        if connected_question is None:
            print("Question not found")
            is_correct = False
            break

        if connected_question["answer"].lower() != answer.answer.lower():
            print("Incorrect")
            is_correct = False
            break

    if is_correct:
        message = "Správně! " + get_hidden_words_zubenka()
    else:
        message = "Špatně!"

    return {"message": message, "is_correct": is_correct}
