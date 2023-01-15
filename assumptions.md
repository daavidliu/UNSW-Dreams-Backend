Assumptions Document
 - record all assumptions made here


variable names for data storage must be consistent between files, so front end code can access the correct values

auth.py
    auth_login_v1 function
        Assume that email not valid return the same error as email not registered

channel.py
    channel_invite_v1 function
        Assume there is no hierarchy between the users inside a channel (eg. owners vs members). 
        All users inside a channel can make invites.
    
When a user creates a channel, they are automatically added to the channel

dm.py
    dm_invite_v1 function
        When a user is added to the dm - the name of the dm remains same even though the user is added to the list of members

    dm_leave_v1 function
        When a user leaves the dm, the name remains the same even though the user id removed from list of members
        If the owner is removed, the 'owner' key value becomes empty.

admin.py
    admin_user_remove function
        when the sole owner of a dm/channel is removed from dreams - no replacement owner is made by the system

message.py

In any function, when the channel ID or DM ID is not metioned, assume that the other is -1 (Similar to message_share)

Assume that Access error message sent by non authoried user and message sent by user not in channel is the same

notifications.py
    Assume that editing a message after it's sent cannot trigger a notification.