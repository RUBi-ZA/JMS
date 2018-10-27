from django.conf import settings
from impersonator.client import Impersonator


def create_session(user):
    config = settings.JMS_SETTINGS["impersonator"]

    client = Impersonator(config["host"], config["port"])

    username = user.userprofile.ssh_user
    private_key = user.userprofile.ssh_private_key
        
    token = client.login(username, private_key=private_key)
    user.userprofile.impersonator_token = token
    user.userprofile.save()
        
    return user


def is_valid_token(client, token, username):
    try:
        client.token = token
        response = client.execute('whoami')
        if response['out'] == '%s\n' % username:
            return True
        else:
            return False
    except Exception as ex:
        print(str(ex))
        return False