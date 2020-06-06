import requests
import logging
import json

def get_dad_joke():
    r = requests.get(
        "https://icanhazdadjoke.com/", headers={"Accept": "text/plain"}
    )
    if r.status_code != 200:
        logging.error("Bad response from cowsay service")
    return r.text


def get_cowsay(text):
    payload = {"msg": text, "f": "default"}
    r = requests.get("https://helloacm.com/api/cowsay/", params=payload)
    if r.status_code != 200:
        logging.error("Bad response from cowsay service")
    t = r.text
    t = json.loads(t)
    return t