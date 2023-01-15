''' 
Tests for the Channels program,
'''
import pytest
import src.channels
import src.channel
import src.auth
import src.other
from src.error import AccessError
from src.error import InputError


# helper function

@pytest.fixture
def setup():
    src.other.clear_v1()
#create a new user, create a new channel belonging to that user, then create a new user and add them to the channel
    auth_user_id = src.auth.auth_register_v1('example@email.com', 'password', 'john', 'smith')
    second_user_id = src.auth.auth_register_v1('example2@email.com', 'password', 'johns', 'smiths')
    new_channel = src.channels.channels_create_v1(auth_user_id['token'], 'testchannel', True)
    new_channel2 = src.channels.channels_create_v1(auth_user_id['token'], 'testchannel2', True)
    return [auth_user_id, second_user_id, new_channel, new_channel2]

#TESTS FOR channels_list_v1
def test_channels_list_v1(setup):
    assert src.channels.channels_list_v1(setup[1]['token']) == {'channels': []}

    # user joins channel 
    src.channel.channel_join_v1(setup[1]['token'], setup[2]['channel_id'])

    assert src.channels.channels_list_v1(setup[1]['token']) == {'channels': [{'channel_id': setup[2]['channel_id'], 'name': 'testchannel'}]}
    
    # create another new channel, user joins channel
    src.channel.channel_join_v1(setup[1]['token'], setup[3]['channel_id'])

    assert src.channels.channels_list_v1(setup[1]['token']) == {'channels': [{'channel_id': setup[2]['channel_id'], 'name': 'testchannel'}, {'channel_id': setup[3]['channel_id'], 'name': 'testchannel2'}]}

    src.other.clear_v1()

def test_not_verified():
    invalid_user_id = 24678

    with pytest.raises(InputError):
        src.channels.channels_list_v1(invalid_user_id)
    
#TESTS FOR channels_listall_v1

def test_channels_listall_v1(setup):
    assert src.channels.channels_listall_v1(setup[1]['token']) == {'channels': [{'channel_id': setup[2]['channel_id'], 'name': 'testchannel'}, {'channel_id': setup[3]['channel_id'], 'name': 'testchannel2'}]}

    src.other.clear_v1()

#TESTS FOR channel_create_v1

#basic tests
def test_channels_create_v1(setup):

    # creat new channel
    src.channels.channels_create_v1(setup[0]['token'], "nameofchannel", True)
    src.channels.channels_create_v1(setup[0]['token'], "nameofchannel", False)

    src.other.clear_v1()

#InputError tests
def test_channels_create_v1_too_long_name(setup):
    # creat new user
    with pytest.raises(InputError):
        src.channels.channels_create_v1(setup[0]['token'], "toolong12345678901234567890", True)

    src.other.clear_v1()

def test_not_verified_create():
    invalid_user_id = 24678

    with pytest.raises(InputError):
        src.channels.channels_create_v1(invalid_user_id, "channelname", True)

#test creating channel with unverified user id
def test_channel_create_v1_unverified(setup):
    unverified_id = 24601
    with pytest.raises(InputError):
        src.channels.channels_create_v1(unverified_id, "channelname", True)

    src.other.clear_v1()

#Succesfull channels create 
def test_channels_created_successfully(setup):

    # get initial number of channels
    channels_list = src.channels.channels_listall_v1(setup[0]['token'])
    initial_count = len(channels_list['channels'])

    # create new channel, confirm number of channels increased by 1
    src.channels.channels_create_v1(setup[0]['token'], "newchannel", True)
    new_channels_list = src.channels.channels_listall_v1(setup[0]['token'])
    final_count = len(new_channels_list['channels'])
    assert final_count == initial_count + 1

    src.other.clear_v1()


