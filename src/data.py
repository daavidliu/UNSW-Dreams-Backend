#Stores all data
import pickle
from datetime import datetime

saveFile = "src/data.p"
try:
    data = pickle.load(open(saveFile,"rb"))
except:
    data = {
        'channels': [], 
        'dms': [], 
        'messages': [], 
        'users': [], 
        'dreams_stats': {
            'channels_exist': [
                {
                    'num_channels_exist': 0, 
                    'time_stamp': datetime.now().timestamp()
                }
            ],
            'dms_exist': [
                {
                    'num_dms_exist': 0, 
                    'time_stamp': datetime.now().timestamp()
                }
            ], 
            'messages_exist': [
                {
                    'num_messages_exist': 0, 
                    'time_stamp': datetime.now().timestamp()
                }
            ], 
            'utilization_rate': 0 
        }
    }

def save_data():
    #saves the data to the pickle file
    pickle.dump(data,open(saveFile,"wb"))


'''
def load_data():
    #loads the data from the stored pickle file, and writes it into data
    print("**********\n \n \n \n \n \n \n \n LOADING THE DATA\n \n \n \n \n \n \n \n **********")
    global data
'''


'''
    users = [
        {'user_id': 1,
        'name_first': 'ansd',
        'name_last': 'asdfads',
        'email' : ,
        'handle_str': 'asdasdasd'
        'session_list' : [],
        'password': 'asdasd',
        'permission_id': 1,
        'notifications': [
            {
                'channel_id': 2,
                'dm_id': -1,
                'notification_message': 'john added you to channel1'
                'time_created': 1582426789,
            }
        ]
        'stats': {
            'channels_joined': [
                {
                    'num_channels_joined': 1, 
                    'time_stamp': 1582426789
                }
            ],
            'dms_joined': [
                {
                    'num_dms_joined': 1, 
                    time_stamp: 1582426789
                }
            ], 
            'messages_sent': [
                {
                    'num_messages_sent': 1, 
                    time_stamp: 1582426789
                }
            ], 
            'involvement_rate': 1 
        }},        
    ]

    channels = [
            {'channel_id': 1,
            'is public' : False,
            "name" :  abc,
            "owner_members" : [user_id list],
            "all_members" : [user_id list],
            'standup_queue_id': -1,
            'standup_time': -1
            }
    ]

    dms = [
        {'dm_id' : 1,
        'name': "handle1, handle2, handle3...",
        'owner' : u_id,
        'members' : [user_id list]   ---> includes owner
        },


    ]

    messages = [
                {
                'message_id': 1,
                'channel_id': 2,
                'dm_id': 3,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        'is_this_user_reacted': False
                    }
                ],
                'is_pinned': False
                },
            ]

    dreams_stats = {
            'channels_exist': [
                {
                    'num_channels_exist': 1, 
                    'time_stamp': 1582426789
                }
            ],
            'dms_exist': [
                {
                    'num_dms_exist': 1, 
                    time_stamp: 1582426789
                }
            ], 
            'messages_exist': [
                {
                    'num_messages_exist': 1, 
                    time_stamp: 1582426789
                }
            ], 
            'utilization_rate': 1 
        }



from src.data import data

userDict = {'user_id': 1,
        'first_name': 'ansd',
        'last_name': 'asdfads',
        'email' : ,
        password:
        }


data['users'].append(userDict)
     owner_id = checked_token['user_id']
    u_ids.insert(0, owner_id)
    all_members = u_ids

'''
