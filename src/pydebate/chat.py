import json

import requests


def loadch(resp):
    return json.loads(
        (resp.strip().removeprefix("```json").removesuffix("```").strip())
    )


def generate(prompt, model="gemma2:2b"):
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "stream": False, "prompt": prompt},
    )
    if res.status_code == 200:
        return res.json()["response"].strip()
    return res


def generate_json(prompt, model="gemma2:2b"):
    for i in range(5):
        try:
            return loadch(generate(prompt, model=model))
        except TypeError:
            pass
        except json.decoder.JSONDecodeError:
            pass
    return None


def chat(messages, tools=None, model="gemma2:2b"):
    if tools is None:
        tools = []
    res = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "messages": messages,
            "model": model,
            "tools": tools,
            "stream": False,
        },
    )
    if res.status_code == 200:
        return res.json()
    return res
