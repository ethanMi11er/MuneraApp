from users.models import User

def create_user(first_name, last_name, email, username, password, alias = None):
        newUser =  User(first_name=first_name, last_name=last_name, email=email, user_name=username, alias=alias)
        newUser.set_password(password)
        newUser.save()
        return newUser

def authenticate_user(*, username, password):
    try:
        user = User.objects.get(user_name=username)
    except User.DoesNotExist:
        return None

    if user.check_password(password):
        return user
    return None
