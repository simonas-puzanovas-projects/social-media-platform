from .user_service import UserService
from .post_service import PostService
from .friendship_service import FriendshipService

user_service = None
post_service = None
friendship_service = None

def init_services(db):
    global user_service
    global post_service
    global friendship_service
    user_service = UserService(db)
    post_service = PostService(db)
    friendship_service = FriendshipService(db)
