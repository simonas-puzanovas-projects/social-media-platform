from .user_service import UserService

user_service = None

def init_services(db):
    global user_service
    user_service = UserService(db)
