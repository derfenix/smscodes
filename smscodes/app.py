import logging

from flask import Flask
from peewee import OperationalError

from smscodes.core import new_code, Codes, NoCodesLeft, check_code, NOT_SENT, use_code, CODE_STATES, count_left, \
    count_unused, pre_generate_codes, NOT_EXISTS, USED
from smscodes.db import db

logger = logging.getLogger('smscodes')

app = Flask(__name__)


def init():
    """Init database and pre-generate codes"""
    records_at_once = 500

    try:
        Codes.select(Codes.code).count()
    except OperationalError:
        db.create_tables([Codes])
        codes = pre_generate_codes()
        Codes.bulk_create(
            [Codes(code=code) for code in codes],
            records_at_once
        )


@app.route('/new/')
def get_new_code():
    try:
        return new_code(), 201
    except NoCodesLeft:
        return "No more codes can be generated", 400


@app.route('/use/<code>/')
def do_use(code: str):
    state = check_code(code)
    if state in (NOT_EXISTS, NOT_SENT):
        return CODE_STATES[state], 404

    if state == USED:
        return "Already used", 400

    if use_code(code) == 0:
        return "OK"
    else:
        return "Failed", 400


@app.route('/check/<code>/')
def do_check(code: str):
    state = check_code(code)
    if state == NOT_EXISTS:
        return '', 404
    return CODE_STATES[state]


@app.route('/left/total/')
def do_count_left():
    return str(count_left())


@app.route('/left/unused/')
def do_count_left_unused():
    return str(count_unused())
