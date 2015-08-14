from django.core.management.base import BaseCommand, make_option

from job.JMS import JMS

import os

from twisted.internet import protocol, reactor, endpoints

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()


class Command(BaseCommand):
    args = '<base_url>'
    help = "Usage: python manage.py setup <base_url>"

    def handle(self, *args, **options):
        endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
        reactor.run()