import bson
import hashlib
from datetime import timedelta
from typing import Optional

from pyramid.request import Request
from pyramid.response import Response

from pypi.bin.load_data import try_int

auth_cookie_name = 'pypi_demo_user'


def set_auth(request: Request, user_id: bson.ObjectId):
    hash_val = __hash_text(str(user_id))
    val = "{}:{}".format(user_id, hash_val)

    request.add_response_callback(lambda req, resp: __add_cookie_callback(
        req, resp, auth_cookie_name, val
    ))


def __hash_text(text: str) -> str:
    text = 'salty__' + text + '__text'
    return hashlib.sha512(text.encode('utf-8')).hexdigest()


def __add_cookie_callback(_, response: Response, name: str, value: str):
    response.set_cookie(name, value, max_age=timedelta(days=30))


def get_user_id_via_auth_cookie(request: Request) -> Optional[bson.ObjectId]:
    if auth_cookie_name not in request.cookies:
        return None

    val = request.cookies[auth_cookie_name]
    parts = val.split(':')
    if len(parts) != 2:
        return None

    user_id = parts[0]
    hash_val = parts[1]
    hash_val_check = __hash_text(user_id)
    if hash_val != hash_val_check:
        print("Warning: Hash mismatch, invalid cookie value")
        return None

    try:
        return bson.ObjectId(user_id)
    except:
        return None


def logout(request: Request):
    request.add_response_callback(lambda req, resp: __delete_cookie_callback(
        resp, auth_cookie_name
    ))


def __delete_cookie_callback(response:Response, name:str):
    response.delete_cookie(name)
