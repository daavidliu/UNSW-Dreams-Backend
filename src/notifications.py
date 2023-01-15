from src.data import data, save_data
from datetime import timezone, datetime

import src.tokenhandler

def notifications_get_v1(token):
    u_id = src.tokenhandler.check_token(token)['user_id']
    notifications = []
    for user in data['users']:
        if user['user_id'] == u_id:
            notifications = user['notifications'].copy()

    #print(notifications)

    #remove notifications that haven't been sent yet
    for notification in notifications:
        if notification['time_created'] > datetime.now().timestamp():
            notifications.remove(notification)

    #Reverse the list so notificatiosn are shown in terms of most recent
    notifications = notifications[::-1]
    #Take the most recent 20 notifications
    notifications = notifications[:20]

    save_data()

    return {'notifications': notifications}