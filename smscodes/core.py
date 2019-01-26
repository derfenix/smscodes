import string
from random import randint

from peewee import SqliteDatabase, Model, FixedCharField, BooleanField

PREGENERATE_CODES_COUNT = 10000

chars = string.ascii_letters + string.digits
chars_count = len(chars)

EXISTS = 1
NOT_EXISTS = 2
USED = 3

CODE_STATES = {
    EXISTS: "exists",
    NOT_EXISTS: "not exists",
    USED: "used"
}
db = SqliteDatabase('db.sqlite3')


class NoCodesLeft(Exception):
    pass


class Codes(Model):
    code = FixedCharField(max_length=4, primary_key=True)
    sent = BooleanField(default=False)
    used = BooleanField(default=False)

    class Meta:
        database = db


def _code_generator():
    """Generate random codes"""
    while True:
        code = []
        for _ in range(4):
            code.append(chars[randint(0, chars_count - 1)])
        yield "".join(code)


def pre_generate_codes():
    """Return set of unique pre-generated codes"""
    g = _code_generator()
    codes = set()
    while len(codes) < PREGENERATE_CODES_COUNT:
        codes.add(next(g))
    g.close()
    return codes


def new_code() -> str:
    """
    Generate, save and return new code

    :raises: NoCodesLeft if there is no code left to be sent
    """
    inst = Codes.select().where(Codes.sent == False).first()
    if inst is None:
        raise NoCodesLeft()
    inst.sent = True
    inst.save()
    return inst.code


def check_code(code: str) -> int:
    """
    Check code's status

    :param code: Code to be checked
    :return: EXISTS (1) if code exists, but not used, NOT_EXISTS (2) if code not exists,
      USED (3) if code exists and used
    """
    query = Codes.select().where(Codes.code == code)
    if not query.exists():
        return NOT_EXISTS
    code_rec = query.get()
    return USED if code_rec.used else EXISTS


def count_left() -> int:
    """Return count of not sent codes"""
    return Codes.select(Codes.code).where(Codes.sent == False).count()


def count_unused() -> int:
    """Return count of generated codes didn't used yet"""
    return Codes.select(Codes.code).where(Codes.used == False).count()


def use_code(code: str) -> bool:
    """
    Mark code as used

    :param code: Code to be marked as used
    :return: True if update success, False if code not found, was not sent or already used
    """
    query = Codes.select().where(Codes.code == code)
    if not query.exists():
        return False

    code_req = query.get()
    if not code_req.sent:
        return False

    if code_req.used:
        return False

    code_req.used = True
    code_req.save()
    return True
