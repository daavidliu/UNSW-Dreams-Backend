import pytest
import requests
import json
from src import auth, config, message, user

#resp = requests.get(config.url + 'echo', params={'data': 'hello'})

@pytest.fixture
def setup():
    requests.delete(config.url + 'clear/v1')

    james_auth = requests.post(config.url + 'auth/register/v2', json={'email' : 'jamesj@gmail.com', 'password' : 'password', 'name_first' : 'James', 'name_last' : 'Jules'})
    first_channel = requests.post(config.url + 'channels/create/v2', json={'token' : james_auth.json()['token'], 'name' : 'James', 'is_public' : True})
    return [james_auth.json(), first_channel.json()]






