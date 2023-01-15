''' 
Tests for the Channel program,
'''
import pytest

import src.channel
import src.auth
import src.channels
import src.other
from src.error import InputError
from src.error import AccessError

#helper functions

# #registers new id from input email and returns the auth_user_id
# def setup_auth(email):
#     auth_user_id = src.auth.auth_register_v1(email, 'password', 'john', 'smith')
#     return auth_user_id['auth_user_id']

# #creates new channel from input parameters and returns the channel_id
# def setup_channel(auth_user_id, name):
#     new_channel = src.channels.channels_create_v1(auth_user_id, name, True)
#     new_channel_id = new_channel['channel_id']
#     return new_channel_id

#test functions
@pytest.fixture
def setup():
    src.other.clear_v1()
    #create a new user, create a new channel belonging to that user, then create a new user and add them to the channel
    auth_user = src.auth.auth_register_v1('example@email.com', 'password', 'john', 'smith')
    second_user = src.auth.auth_register_v1('example2@email.com', 'password', 'johns', 'smiths')
    new_channel = src.channels.channels_create_v1(auth_user['token'], 'testchannel', True)
    return [auth_user, second_user, new_channel]

def test_channel_invite_valid(setup):
    assert src.channel.channel_invite_v1(setup[0]['token'], setup[2]['channel_id'], setup[1]['auth_user_id']) == {}

    assert src.channels.channels_list_v1(setup[0]['token']) == {
        'channels': [{'channel_id': setup[2]['channel_id'], 'name': 'testchannel'}]
    }
def test_channel_invite_users(setup):
    #second user is not in any channels
    assert src.channels.channels_list_v1(setup[1]['token']) == {'channels': []}

    #check that invite function returns empty dictionary
    assert src.channel.channel_invite_v1(setup[0]['token'], setup[2]['channel_id'], setup[1]['auth_user_id']) == {}

    #check that the user is in new_channel
    assert src.channels.channels_list_v1(setup[1]['token']) == {
        'channels': [{'channel_id': setup[2]['channel_id'], 'name': 'testchannel'}]
    }

    src.other.clear_v1()

#test if correct input errors are produced with invlalid auth user inputs 
def test_channel_invite_auth_error(setup):
    invalid_token = 'invalidToken'
    with pytest.raises(InputError):
        src.channel.channel_invite_v1(invalid_token, setup[2]['channel_id'], setup[1]['auth_user_id'])


    src.other.clear_v1()

#test if correct input errors are produced with invlalid user inputs 
def test_channel_invite_user_error(setup):
    invalid_id = -10000
    with pytest.raises(InputError):
        src.channel.channel_invite_v1(setup[0]['token'], setup[2]['channel_id'], invalid_id)
    with pytest.raises(InputError):
        src.channel.channel_invite_v1(setup[0]['token'], setup[2]['channel_id'], invalid_id)

    #error when the inviting user is not in the channel
    with pytest.raises(AccessError):
        src.channel.channel_invite_v1(setup[1]['token'], setup[2]['channel_id'], setup[1]['auth_user_id'])

    #inviting user who already exists in channel does nothing
    assert src.channel.channel_invite_v1(setup[0]['token'], setup[2]['channel_id'], setup[0]['auth_user_id']) == {}
        
    src.other.clear_v1()

##test if correct input errors are produced with invlalid channel inputs 
def test_channel_invite_channel_error(setup):
    with pytest.raises(InputError):
        src.channel.channel_invite_v1(setup[0]['token'], -10000, setup[1]['auth_user_id'])

    src.other.clear_v1()
    
#test the channel_messages funciton
def test_channel_messages(setup):
    #tests for channel_messages
    with pytest.raises(InputError):
        src.channel.channel_messages_v1('invalidToken', setup[2]['channel_id'], 0) #invalid auth_user_is

    with pytest.raises(InputError):
        src.channel.channel_messages_v1(setup[0]['token'], -10000, 0)  #invalid channel_id
    
    src.other.clear_v1()



#test the channel join funcion
def test_channel_join(setup):

    user2 = src.auth.auth_register_v1('notemail@gmail.com', 'passwordz', 'johns', 'smiths')
    channel_name = src.channels.channels_create_v1(user2['token'], 'New Channel', True)
    
    assert src.channel.channel_join_v1(user2['token'], channel_name['channel_id']) == {} #Joined channel successfully

    channel_name2 = src.channels.channels_create_v1(user2['token'], 'New Channel2', False)

    with pytest.raises(AccessError):
        src.channel.channel_join_v1(user2['token'], channel_name2['channel_id']) #Channel is not public

    src.other.clear_v1()

#test the channel join funcion produces InputError with invalid channel_id
def test_channel_join_idNotFound(setup):
    invalid_id = 75839484
    with pytest.raises(InputError):
        src.channel.channel_join_v1(setup[0]['token'], invalid_id)
        
    src.other.clear_v1()

def test_auth_user_not_in_channel(setup):

    with pytest.raises(AccessError):
        src.channel.channel_details_v1(setup[1]['token'], setup[2]['channel_id'])

#test the channel details function
def test_channel_details_ID_presence(setup):
    invalid_token = 'invalidToken'
    invalid_id = -24601
    #test for access error 
    with pytest.raises(InputError):
        src.channel.channel_details_v1(setup[0]['token'], invalid_id)
    with pytest.raises(InputError):
        src.channel.channel_details_v1(invalid_token, setup[2]['channel_id'])

    src.other.clear_v1()

#test if the correct details are returned
def test_channel_details(setup):
    # Generated auth_user id and temporary channel
    assert src.channel.channel_details_v1(setup[0]['token'], setup[2]['channel_id']) == {
        'name': 'testchannel',
        'is_public': True, 
        'owner_members': [
            {
                'email': 'example@email.com',
                'handle_str': 'johnsmith',
                'name_first': 'john',
                'name_last': 'smith',
                'u_id': 1,
                'profile_img_url' : '',
            }
        ], 
        'all_members': [
            {
                'email': 'example@email.com',
                'handle_str': 'johnsmith',
                'name_first': 'john',
                'name_last': 'smith',
                'u_id': 1,
                'profile_img_url' : '',
            }
        ]
    }

    src.other.clear_v1()

#test channel messages 
def test_channel_messages_invalid_inputs(setup):
    invalid_token = 'invalidToken'
    invalid_id = 24601
    with pytest.raises(InputError):
        src.channel.channel_messages_v1(invalid_token, setup[2]['channel_id'], 0)
    with pytest.raises(InputError):
        src.channel.channel_messages_v1(setup[0]['token'], invalid_id, 0)

    #access error, user is not part of the channel
    with pytest.raises(AccessError):
        src.channel.channel_messages_v1(setup[1]['token'], setup[2]['channel_id'], 0)
    #input error, start is greater than total number of messages
    with pytest.raises(InputError):
        src.channel.channel_messages_v1(setup[0]['token'], setup[2]['channel_id'], 1)

    assert src.channel.channel_messages_v1(setup[0]['token'], setup[2]['channel_id'], 0) == {'messages': [], 'start': 0, 'end': -1}

################################## remove ##################################
#test channel_removeOwner
def test_channel_removeowner_v1(setup):
    src.channel.channel_addowner_v1(setup[0]['token'], setup[2]['channel_id'], setup[1]['auth_user_id'])
    new_owner = src.auth.auth_register_v1('limba@bim.com', 'password', 'lim', 'ba')
    src.channel.channel_addowner_v1(setup[0]['token'],setup[2]['channel_id'],new_owner['auth_user_id'] )
    assert src.channel.channel_removeowner_v1(setup[0]['token'], setup[2]['channel_id'], setup[1]['auth_user_id']) == {}
    src.other.clear_v1()
    #the ower has added u_id sucessfully

def test_channel_remChannelId_notValid(setup):
    #checks inputerror, if channel is not valid
    invalidID = 549875078
    with pytest.raises(InputError):
        src.channel.channel_removeowner_v1(setup[0]['token'], setup[1]['token'],invalidID)

    src.other.clear_v1

def test_channel_remChannel_user_is_owner(setup):
    #checks inputerror, if u_id is already an owner
    owner_user = src.auth.auth_register_v1('mimbim@gmail.com', 'password', 'mim', 'bim')
    owners_chanel = src.channels.channels_create_v1(owner_user['token'], 'his channel', True)
    with pytest.raises(InputError):
        src.channel.channel_removeowner_v1(owner_user['token'], owners_chanel['channel_id'], owner_user['token'])

    owner_user2 = src.auth.auth_register_v1('kimbim@gmail.com', 'password', 'kim', 'bim')
    src.channel.channel_addowner_v1(owner_user['token'], owners_chanel['channel_id'], owner_user2["auth_user_id"])
    with pytest.raises(InputError):
        src.channel.channel_removeowner_v1(owner_user['token'], owners_chanel['channel_id'], setup[1]['auth_user_id'])   

    src.other.clear_v1()

#################################################### NOT dreme user #####################
def test_channel_authUser_notDreamUser(setup):
    #checks acess error, if the auth_user_id/owner user is not part of dreams
    fake_user = 'invalid_token'
    with pytest.raises(InputError):
        src.channel.channel_addowner_v1(fake_user, setup[2]['channel_id'], setup[1]['auth_user_id'])
    fake_user2 = 'invalid_token'
    with pytest.raises(InputError):
        src.channel.channel_removeowner_v1(fake_user2, setup[2]['channel_id'], setup[1]['auth_user_id'])
    
    src.other.clear_v1
####################################################  ADD ################################
#test channel_addowner
def test_channel_addowner_v1(setup):
    assert src.channel.channel_addowner_v1(setup[0]['token'], setup[2]['channel_id'], setup[1]['auth_user_id']) == {}
    src.other.clear_v1()
    #the ower has added u_id sucessfully

def test_channel_addChannelId_notValid(setup):
    #checks inputerror, if channel is not valid
    invalidID = 549875078
    with pytest.raises(InputError):
        src.channel.channel_addowner_v1(setup[0]['token'], setup[1]['token'],invalidID)

    src.other.clear_v1

def test_channel_addChannel_user_is_owner(setup):
    #checks inputerror, if u_id is already an owner
    owner_user = src.auth.auth_register_v1('email@gmail.com', 'password', 'mim', 'bim')
    owners_chanel = src.channels.channels_create_v1(owner_user['token'], 'his channel', True)

    with pytest.raises(InputError):
        src.channel.channel_addowner_v1(owner_user['token'], owners_chanel['channel_id'], owner_user['auth_user_id'])

    owner_user2 = src.auth.auth_register_v1('kimbim@gmail.com', 'password', 'kim', 'bim')
    src.channel.channel_addowner_v1(owner_user['token'], owners_chanel['channel_id'], owner_user2['auth_user_id'])
    with pytest.raises(InputError):
        src.channel.channel_addowner_v1(owner_user['token'], owners_chanel['channel_id'], owner_user2['auth_user_id'])   

    src.other.clear_v1()
############################################# leave ################################
#test channel_leve function
def test_channel_leave_v1(setup):
    user2 = src.auth.auth_register_v1('notemail@gmail.com', 'passwordz', 'johns', 'smiths')
    channel_name = src.channels.channels_create_v1(user2['token'], 'New Channel', True)
    assert src.channel.channel_leave_v1(user2['token'], channel_name['channel_id']) == {} #left channel sucessfuly

    src.other.clear_v1()

def test_chanel_auth_userid_not_valid(setup):
    invalidID = 640876
    with pytest.raises(InputError):
        src.channel.channel_leave_v1(setup[0]['token'], invalidID)

    src.other.clear_v1()


def test_chanel_auth_user_notPartOfChannel (setup):
    not_user = src.auth.auth_register_v1('deepanshu@babab.com', 'password', 'deepufirst', 'deepulast')
    channel_other = src.channels.channels_create_v1(not_user['token'], 'other channel', True)
    
    with pytest.raises(AccessError):
        assert src.channel.channel_leave_v1(setup[0]['token'], channel_other['channel_id']) 

    src.other.clear_v1()
