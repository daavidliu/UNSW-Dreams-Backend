''' 
Tests for the Token program,
'''
from re import T
import pytest

import src.tokenhandler
import src.other
import src.auth
from src.error import InputError
from src.error import AccessError

@pytest.fixture
def setup():
    src.other.clear_v1()
    auth_user_id = src.auth.auth_register_v1('example@email.com', 'password', 'john', 'smith')
    return auth_user_id

def test_encoding():
    src.other.clear_v1()
    out = src.tokenhandler.encode_message({"session_id" : 1})
    assert out == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uX2lkIjoxfQ.oqcviRQcCr1eIhmM7UCdwmj0WIyIXIUTCmvwW7kFk5s"

def test_decoding():
    src.other.clear_v1()
    out = src.tokenhandler.decode_message("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uX2lkIjoyfQ.wu_HmJUvPSlB75IdMXF359GXetbjq4z-5lqXV1djw6A")
    assert out == {"session_id": 2}

def test_generate_token():
    src.other.clear_v1()
    out = src.tokenhandler.generate_token({"session_id" : 1})
    assert out == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uX2lkIjoxfQ.oqcviRQcCr1eIhmM7UCdwmj0WIyIXIUTCmvwW7kFk5s"
    src.other.clear_v1()

def test_check_token(setup):
    
    token = src.tokenhandler.generate_token({"session_id" : 1})
    assert src.tokenhandler.check_token(token) == {'user_id': setup['auth_user_id'], 'session_id': 1}
    src.other.clear_v1()