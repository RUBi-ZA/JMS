import requests, json


class Impersonator(object):

    def __init__(self, host = "127.0.0.1", port = 31000, token=None, token_endpoint="tokens", command_endpoint=""):
        self.host = host
        self.port = port
        self.token = token
        self.token_endpoint = token_endpoint
        self.command_endpoint = command_endpoint

    def login(self, username, password):
        endpoint = "http://%s:%d/%s" % (self.host, self.port, self.token_endpoint)
        payload = {
            "username": username,
            "password": password
        }

        r = requests.post(endpoint, json=payload)

        if r.status_code == requests.codes.ok:
            self.token =  r.text
        else:
            raise Exception(r.text)

        return self.token

    def logout(self):
        if self.token:
            endpoint = "http://%s:%d/%s/%s" % (self.host, self.port, self.token_endpoint, self.token)

            r = requests.delete(endpoint)

            if r.status_code == requests.codes.ok:
                self.token = None
            else:
                raise Exception(r.text)

    def execute(self, command):
        endpoint = "http://%s:%d/%s" % (self.host, self.port, self.command_endpoint)
        payload = {
            "token": self.token,
            "command": command
        }

        r = requests.post(endpoint, json=payload)

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            raise Exception(r.text)
