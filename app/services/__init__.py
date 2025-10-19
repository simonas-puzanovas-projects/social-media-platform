from .user_service import UserService
from .post_service import PostService
from .friendship_service import FriendshipService
from .notifcation_service import NotificationService
from .user_settings_service import UserSettingsService

user_service = None
post_service = None
friendship_service = None
notification_service = None
user_settings_service = None

def init_services(db):

    global user_service
    global post_service
    global friendship_service
    global notification_service
    global user_settings_service

    user_service = UserService(db)
    post_service = PostService(db)
    friendship_service = FriendshipService(db)
    notification_service = NotificationService(db)
    user_settings_service = UserSettingsService(db)
