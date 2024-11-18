import os
import functools
import inspect
from typing import Any as LiterallyAnything

from openai import OpenAI


MODEL = "gpt-4o-mini"
API_KEY = os.environ.get("OPENAI_API_KEY")


client = OpenAI(api_key=API_KEY)


def add(a: LiterallyAnything, b: LiterallyAnything) -> float | None:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a mathematics teacher."},
            {
                "role": "user",
                "content": f"What is {a} + {b}? Output the NUMBER ONLY.",
            },
        ],
    )
    return float(res) if (res := completion.choices[0].message.content) else None


def fib(n: int) -> int | None:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a mathematician."},
            {
                "role": "user",
                "content": f"Calculate the {n}th Fibonacci number. "
                "Output the NUMBER ONLY.",
            },
        ],
    )
    return int(res) if (res := completion.choices[0].message.content) else None


def gt(a: LiterallyAnything, b: LiterallyAnything) -> bool | None:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a lot of things, but most imporantly a python developer, which you love.",
            },
            {
                "role": "user",
                "content": f"According to you, is {a} greater than {b}? Output 'yes' or 'no' WIHTOUT ANY COMMENTS."
                "interpret 'greater' in any way you like (better/taller/longer/etc).",
            },
        ],
    )
    resp = completion.choices[0].message.content
    assert resp is not None
    return "yes" in resp.lower()


def matches(text: str, pattern: str) -> bool | None:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a regex master and a pattern matcher in general.",
            },
            {
                "role": "user",
                "content": f"Does the text '{text}' match the pattern '{pattern}'? Output 'yes' or 'no' WITHOUT ANY COMMENTS.",
            },
        ],
    )
    resp = completion.choices[0].message.content
    assert resp is not None
    return "yes" in resp.lower()


def ast(code_text: str) -> str:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are the python interpreter."},
            {
                "role": "user",
                "content": f"Construct an abstract syntax tree for the following code and style it pretty:\n{code_text}\n"
                "DONT WRITE ANY CLARIFICATIONS OR COMMENTS, JUST THE AST.",
            },
        ],
    )
    return completion.choices[0].message.content or ""


def is_good_date_time_string(dt_str: str) -> tuple[bool, str]:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a date and time validator."},
            {
                "role": "user",
                "content": f"Check if the following string is a valid datetime according to RFC3339:\n{dt_str}\n"
                "If there is no timezone information, consider the format invalid. "
                "Output 'yes' or 'no'. Then give a brief explanation.",
            },
        ],
    )
    resp = completion.choices[0].message.content
    assert resp is not None
    return "yes" in resp.lower(), resp


def advise(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        prompt = f"""A function
        {inspect.getsource(func)}
        has benn called with
        the arguments {args} and the keyword arguments {kwargs}
        and returned {res}.
        
        Give a comment explaining what it might do.
        """
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a code reviewer."},
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        resp = completion.choices[0].message.content
        print(resp)
        return res

    return wrapper
