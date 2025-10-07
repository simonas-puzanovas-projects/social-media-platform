from ..models import Notification
from flask import json

class NotificationServiceError(Exception): pass

class NotificationService:
    def __init__(self, db):
        self.db = db

    def query_notifications(self, user_id, type=None):
        try:
            if type:
                print("with type")
                return Notification.query.filter_by(
                    user_id=user_id,
                    type=type
                ).all()
                
            else:
                return Notification.query.filter_by(
                    user_id=user_id,
                ).all()
        
        except Exception as e:
            print("with type error")
            raise NotificationServiceError(e)
        
    
    def remove_friendship_history(self, user_0, user_1, friendship_id):
        query_array = [
            self.query_notifications(user_0, "friend_request"),
            self.query_notifications(user_1, "friend_request")
        ]

        for user_query in query_array:
            try:
                for notification in user_query:
                    data = json.loads(notification.data)
                    if data and data.get('friendship_id') == friendship_id:
                        self.db.session.delete(notification)
                self.db.session.commit()

            except Exception as e:
                self.db.rollback()
                raise NotificationServiceError(e)





