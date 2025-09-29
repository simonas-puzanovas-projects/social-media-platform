from .user_service import UserService
from .post_service import PostService

user_service = None

def init_services(db):
    global user_service
    global post_service
    user_service = UserService(db)
    post_service = PostService(db)
