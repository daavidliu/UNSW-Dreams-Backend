import pytest

import src.dm
import src.auth
import src.other
from src.error import InputError
from src.error import AccessError


#helper function
@pytest.fixture
def setup():
    src.other.clear_v1()

    first_user_id = src.auth.auth_register_v1('example@email.com', 'password', 'john', 'smith')
    second_user_id = src.auth.auth_register_v1('example2@email.com', 'password', 'maggie', 'smith')
    third_user_id = src.auth.auth_register_v1('example3@email.com', 'password', 'Sam', 'smith')

    return[first_user_id, second_user_id, third_user_id]



#TESTS for dm_create_v1
def test_dm_create_error():
    invalid_id = 123456
    with pytest.raises(InputError):
        src.dm.dm_create_v1(invalid_id, [])

    src.other.clear_v1()

def test_dm_create_success(setup):
    #create a new dm without third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])
    assert new_dm['dm_name'] == 'johnsmith,maggiesmith'
    assert new_dm['dm_id'] == 1

    #creating a new dm with just owner 
    add_dm = src.dm.dm_create_v1(setup[0]['token'],[]) 
    assert add_dm['dm_id'] == 2
    assert add_dm['dm_name'] == 'johnsmith'

    #creating a new dm with second_user as owner and third user as memeber
    add_dm1 = src.dm.dm_create_v1(setup[1]['token'],[setup[2]['auth_user_id']])
    assert add_dm1['dm_id'] == 3
    assert add_dm1['dm_name'] == 'maggiesmith,samsmith'

    src.other.clear_v1()

def test_dm_create_success1(setup):
    #create a new dm with third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id'], setup[2]['auth_user_id']])

    assert new_dm['dm_id'] == 1
    assert new_dm['dm_name'] == 'johnsmith,maggiesmith,samsmith'

    src.other.clear_v1()

#if any u_id in u_ids list is invalid 
def test_dm_create_invalid(setup):
    invalid_u_id = 1234567
    with pytest.raises(InputError):
        src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id'], invalid_u_id])



#TESTS for dm_details_v1
def test_dm_details_error(setup):
    invalidToken = 'invalidToken'
    invalid_id = -2083645

    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    #invalid_dm_id
    with pytest.raises(InputError):
        src.dm.dm_details_v1(setup[0]['token'], invalid_id)
    
    #invalid token
    with pytest.raises(InputError):
        src.dm.dm_details_v1(invalidToken, new_dm['dm_id'])
    
    #user not member of dm
    with pytest.raises(AccessError):
        src.dm.dm_details_v1(setup[2]['token'], new_dm['dm_id'])


    src.other.clear_v1()

def test_dm_details_success(setup):
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])
    dm1 = src.dm.dm_details_v1(setup[0]['token'], new_dm['dm_id'])
    name = dm1['name']
    memebers = dm1['members']
    
    assert name == 'johnsmith,maggiesmith'
    assert memebers == [
        {
            'email': 'example2@email.com',
            'handle_str': 'maggiesmith',
            'name_first': 'maggie',
            'name_last': 'smith',
            'u_id': 2,
            'profile_img_url' : '',
        },
        {
            'email': 'example@email.com',
            'handle_str': 'johnsmith',
            'name_first': 'john',
            'name_last': 'smith',
            'u_id': 1,
            'profile_img_url' : '',
        }
    ]

    src.other.clear_v1()



#TESTS for dm_list_v1 which also tests dm_invite_v1

#success
def test_dm_invite_v1(setup):
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    assert src.dm.dm_invite_v1(setup[0]['token'], new_dm['dm_id'], setup[1]['auth_user_id']) == {}
    
    list1 = src.dm.dm_list_v1(setup[0]['token'])
    dms1 = list1['dms']

    assert dms1 == [{'dm_id': new_dm['dm_id'], 'name': 'johnsmith,maggiesmith'}]
    src.other.clear_v1()


def test_dm_list_v1(setup):
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])
    
    assert src.dm.dm_list_v1(setup[2]['token']) == {'dms': []}
    assert src.dm.dm_invite_v1(setup[0]['token'], new_dm['dm_id'], setup[2]['auth_user_id']) == {}

    list1 = src.dm.dm_list_v1(setup[2]['token'])
    dms1 = list1['dms']

    assert dms1 == [{'dm_id': new_dm['dm_id'], 'name': 'johnsmith,maggiesmith'}]
    src.other.clear_v1()
   
#errors

#invalid user_id input for dm_list_v1
def test_invalid_user_list():
    invalid_user_id = 1234567

    with pytest.raises(InputError):
        src.dm.dm_list_v1(invalid_user_id)
    
    src.other.clear_v1()

#input is an invalid token for both
def test_invalid_token(setup):
    #create a new dm without third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    invalid_token = 'invalidToken'
    with pytest.raises(InputError):
        src.dm.dm_invite_v1(invalid_token, new_dm['dm_id'], setup[1]['auth_user_id'])

    with pytest.raises(InputError):
        src.dm.dm_list_v1(invalid_token)
    
    src.other.clear_v1()

#invalid user inputs for dm_invite_v1
def test_not_verified_invite(setup):
    #create a new dm without third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    #invalid u_id (user not registered)
    invalid_id = -12345
    with pytest.raises(InputError):
        src.dm.dm_invite_v1(setup[0]['token'], new_dm['dm_id'], invalid_id)

    #error when the inviting user(token user) is not in the dm
    with pytest.raises(AccessError):
        src.dm.dm_invite_v1(setup[2]['token'], new_dm['dm_id'], setup[1]['auth_user_id'])

    #inviting user who already exists in dm 
    assert src.dm.dm_invite_v1(setup[0]['token'], new_dm['dm_id'], setup[0]['auth_user_id']) == {}
        
    src.other.clear_v1()

#if dm_id is invalid
def test_dm_invite_error(setup):
    #create a new dm without third user
    src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    with pytest.raises(InputError):
        src.dm.dm_invite_v1(setup[0]['token'], -10000, setup[1]['auth_user_id'])

    src.other.clear_v1()


#TESTS for dm_remove_v1

#success
def test_dm_remove_success(setup):
    #create a new dm without third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    assert src.dm.dm_list_v1(setup[2]['token']) == {'dms': []}
    assert src.dm.dm_invite_v1(setup[0]['token'], new_dm['dm_id'], setup[2]['auth_user_id']) == {}

    list1 = src.dm.dm_list_v1(setup[2]['token'])
    dms1 = list1['dms']

    #name doesn't change 
    assert dms1 == [{'dm_id': new_dm['dm_id'], 'name': 'johnsmith,maggiesmith'}]

    assert src.dm.dm_remove_v1(setup[0]['token'], new_dm['dm_id']) == {}
    
    #list for both the memebers
    assert src.dm.dm_list_v1(setup[0]['token']) == {'dms': []}
    assert src.dm.dm_list_v1(setup[1]['token']) == {'dms': []}

    src.other.clear_v1()

#error
def test_dm_remove_error(setup):
    #create a new dm without third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    #invalid token
    invalid_token = 'invalidToken'
    with pytest.raises(InputError):
        src.dm.dm_remove_v1(invalid_token, new_dm['dm_id'])

    #invalid dm_id
    with pytest.raises(InputError):
        src.dm.dm_remove_v1(setup[0]['token'], -10000)
    
    #not the creator
    with pytest.raises(AccessError):
        src.dm.dm_remove_v1(setup[1]['token'],new_dm['dm_id'] )
     
    src.other.clear_v1()

#TESTS for dm_leave_v1

#success
def test_dm_leave_v1(setup):
    #create a new dm without third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    assert src.dm.dm_list_v1(setup[2]['token']) == {'dms': []}
    assert src.dm.dm_invite_v1(setup[0]['token'], new_dm['dm_id'], setup[2]['auth_user_id']) == {}

    list1 = src.dm.dm_list_v1(setup[2]['token'])
    dms1 = list1['dms']

    assert dms1 == [{'dm_id': new_dm['dm_id'], 'name': 'johnsmith,maggiesmith'}]

    assert src.dm.dm_leave_v1(setup[0]['token'], new_dm['dm_id']) == {}
    
    assert src.dm.dm_list_v1(setup[1]['token']) == {'dms': [{'dm_id': 1, 'name': 'johnsmith,maggiesmith'}]}
    assert src.dm.dm_list_v1(setup[0]['token']) == {'dms': []}

    src.other.clear_v1()

#errors
def test_dm_leave_v1_error(setup):
    #create a new dm without third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    #invalid token
    invalid_token = 'invalidToken'
    with pytest.raises(InputError):
        src.dm.dm_leave_v1(invalid_token, new_dm['dm_id'])

    #invalid dm_id
    with pytest.raises(InputError):
        src.dm.dm_leave_v1(setup[0]['token'], -10000)

    #authorised user is not a member of dm
    with pytest.raises(AccessError):
        src.dm.dm_leave_v1(setup[2]['token'],new_dm['dm_id'])
     
    src.other.clear_v1()

#TESTS for dm_messages_v1

#errors
def test_dm_messages_invalid_inputs(setup):
    #create a new dm without third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    invalid_token = 'invalidToken'
    invalid_id = 345678
    with pytest.raises(InputError):
        src.dm.dm_messages_v1(invalid_token, new_dm['dm_id'], 0)
    with pytest.raises(InputError):
        src.dm.dm_messages_v1(setup[0]['token'], invalid_id, 0)

    #access error, user is not part of the dm
    with pytest.raises(AccessError):
        src.dm.dm_messages_v1(setup[2]['token'], new_dm['dm_id'], 0)
    #input error, start is greater than total number of messages
    with pytest.raises(InputError):
        src.dm.dm_messages_v1(setup[0]['token'], new_dm['dm_id'], 1)

    assert src.dm.dm_messages_v1(setup[0]['token'], new_dm['dm_id'], 0) == {'messages': [], 'start': 0, 'end': -1}

#success
def test_dm_messages(setup):
    #create a new dm without third user
    new_dm = src.dm.dm_create_v1(setup[0]['token'],[setup[1]['auth_user_id']])

    #tests for dm_messages
    with pytest.raises(InputError):
        src.dm.dm_messages_v1('invalidToken', new_dm['dm_id'], 0) #invalid auth_user_id

    with pytest.raises(InputError):
        src.dm.dm_messages_v1(setup[0]['token'], -10000, 0)  #invalid dm_id
    
    src.other.clear_v1()

    
