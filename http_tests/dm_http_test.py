''' 
HTTP Tests for the dm program,
'''
from werkzeug.exceptions import BadRequest
from src import error
from src.error import InputError
from src.error import AccessError
import pytest
import requests
import json
from src import auth, config, dm


@pytest.fixture
def setup():
    requests.delete(config.url + 'clear/v1')
    
    first_user_id = requests.post(config.url + 'auth/register/v2', json = {'email' : 'example@email.com', 'password' : 'password', 'name_first' : 'john', 'name_last' : 'smith'})
    second_user_id = requests.post(config.url + 'auth/register/v2', json = {'email' : 'example2@email.com', 'password' : 'password', 'name_first' : 'maggie', 'name_last' : 'smith'})
    third_user_id = requests.post(config.url + 'auth/register/v2', json = {'email' : 'example3@email.com', 'password' : 'password', 'name_first' : 'Sam', 'name_last' : 'smith'})
    return[first_user_id, second_user_id, third_user_id]

def test_dm_create_invalid(setup):
    invalid_u_id = 1234567
    result = requests.post(config.url + "dm/create/v1", json = {"token" : setup[0].json()["token"], "u_ids" : [setup[1].json()["auth_user_id"], invalid_u_id]} )
    assert result.json()['name'] == 'System Error'
    requests.delete(config.url + "clear/v1")

#TESTS for dm_details_v1
def test_dm_details_error(setup):
    invalidToken = 'invalidToken'
    invalid_id = -2083645

    new_dm = requests.post(config.url + "dm/create/v1", json = {"token" : setup[0].json()["token"], "u_ids" : [setup[1].json()["auth_user_id"]]} )
    result = requests.get(config.url + "dm/details/v1", params = {"token" : setup[0].json()["token"], "dm_id" : invalid_id})
    assert result.json()['name'] == 'System Error'

    result2 = requests.get(config.url + "dm/details/v1", params = {"token" : invalidToken, "dm_id" : new_dm.json()['dm_id']})
    assert result2.json()['name'] == 'System Error'

    requests.delete(config.url + "clear/v1")

def test_dm_details_success(setup):
    new_dm = requests.post(config.url + "dm/create/v1", json = {"token" : setup[0].json()["token"], "u_ids" : [setup[1].json()["auth_user_id"]]} )
    new_dm_id = new_dm.json()['dm_id']
    result = requests.get(config.url + "dm/details/v1", params = {"token" : setup[0].json()["token"], "dm_id" : new_dm_id})
    assert result.json()["name"] == 'johnsmith,maggiesmith'
    requests.delete(config.url + "clear/v1")


def test_invalid_user_list(setup):
    invalid_user_id = 1234567
    invalid_token = 'invalidToken'

    new_dm = requests.post(config.url + "dm/create/v1", json = {"token" : setup[0].json()["token"], "u_ids" : [setup[1].json()["auth_user_id"]]} )
    result = requests.get(config.url + "dm/invite/v1", params={'token' : invalid_token, 'dm_id' : new_dm.json()['dm_id'], 'u_id' : invalid_user_id})
    assert result.json()['name'] == 'System Error'
    requests.delete(config.url + 'clear/v1')


def test_dm_list_v1(setup):
    new_dm = requests.post(config.url + "dm/create/v1", json = {"token" : setup[0].json()["token"], "u_ids" : [setup[1].json()["auth_user_id"]]} )
    
    assert requests.get(config.url + "dm/list/v1", params={'token' : setup[2].json()['token']}).json() == {'dms': []}
    requests.post(config.url + "dm/invite/v1", json= {'token' : setup[0].json()['token'], 'dm_id' : new_dm.json()['dm_id'], 'u_id' : setup[2].json()['auth_user_id'] })

    assert requests.get(config.url + "dm/list/v1", params={'token' : setup[2].json()['token']}).json() == {'dms' : [{'dm_id': new_dm.json()['dm_id'], 'name': 'johnsmith,maggiesmith'}]}
    requests.delete(config.url + 'clear/v1')

def test_not_verified():
    invalid_user_id = 24678

    result = requests.get(config.url + "dm/list/v1", params={'token' : invalid_user_id})
    assert result.json()['name'] == 'System Error'
    requests.delete(config.url + 'clear/v1')

def test_dm_remove(setup):
    new_dm = requests.post(config.url + "dm/create/v1", json = {"token" : setup[0].json()["token"], "u_ids" : [setup[1].json()["auth_user_id"]]} )
    requests.post(config.url + "dm/invite/v1", json= {'token' : setup[0].json()['token'], 'dm_id' : new_dm.json()['dm_id'], 'u_id' : setup[2].json()['auth_user_id'] })

    requests.delete(config.url + "dm/remove/v1", json= {'token' : setup[0].json()['token'], 'dm_id' : new_dm.json()['dm_id']}) 

    assert requests.get(config.url + "dm/list/v1", params={'token' : setup[2].json()['token']}).json() == {'dms': []}
    requests.delete(config.url + 'clear/v1')

def test_dm_remove_error(setup):
    invalid_token = 'invalidToken'
    result = requests.get(config.url + "dm/remove/v1", params={'token' : invalid_token, 'dm_id' : -10000})
    assert result.json()['name'] == 'System Error'
    requests.delete(config.url + 'clear/v1')

def test_dm_leave_v1(setup):
    #create a new dm without third user
    new_dm = requests.post(config.url + "dm/create/v1", json = {"token" : setup[0].json()["token"], "u_ids" : [setup[1].json()["auth_user_id"]]} )

    assert requests.get(config.url + "dm/list/v1", params={'token' : setup[2].json()['token']}).json() == {'dms': []}
    assert requests.post(config.url + "dm/invite/v1", json= {'token' : setup[0].json()['token'], 'dm_id' : new_dm.json()['dm_id'], 'u_id' : setup[2].json()['auth_user_id'] }).json() == {}

    list1 = requests.get(config.url + "dm/list/v1", params={'token' : setup[2].json()['token']}).json()
    dms1 = list1['dms']

    assert dms1 == [{'dm_id': new_dm.json()['dm_id'], 'name': 'johnsmith,maggiesmith'}]

    result = requests.post(config.url + 'dm/leave/v1', json={'token' : setup[0].json()['token'], 'dm_id' : new_dm.json()['dm_id']})
    assert result.json() == {}
    
    assert requests.get(config.url + "dm/list/v1", params={'token' : setup[1].json()['token']}).json() == {'dms': [{'dm_id': 1, 'name': 'johnsmith,maggiesmith'}]}
    assert requests.get(config.url + "dm/list/v1", params={'token' : setup[0].json()['token']}).json() == {'dms': []}

    requests.delete(config.url + 'clear/v1')

#errors
def test_dm_leave_v1_error(setup):
    #create a new dm without third user
    new_dm = requests.post(config.url + "dm/create/v1", json = {"token" : setup[0].json()["token"], "u_ids" : [setup[1].json()["auth_user_id"]]} )

    #invalid token
    invalid_token = 'invalidToken'
    result = requests.post(config.url + 'dm/leave/v1', json={'token' : invalid_token, 'dm_id' : new_dm.json()['dm_id']})
    assert result.json()['code'] == 400

    #invalid dm_id
    invalid_dm_id = -10000
    result = requests.post(config.url + 'dm/leave/v1', json={'token' : setup[0].json()["token"], 'dm_id' : invalid_dm_id})
    assert result.json()['code'] == 400

    #authorised user is not a member of dm
    result = requests.post(config.url + 'dm/leave/v1', json={'token' : setup[2].json()["token"], 'dm_id' : new_dm.json()['dm_id']})
    assert result.json()['code'] == 403
     
    requests.delete(config.url + 'clear/v1') 





