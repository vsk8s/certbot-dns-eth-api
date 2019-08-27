import logging
import grpc

import zope.interface

from certbot import interfaces
from certbot.plugins import dns_common

import certbot_dns_eth_api.dnsapi_pb2_grpc as api_grpc
import certbot_dns_eth_api.dnsapi_pb2 as api

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    description = ""
    long_description = ""

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(add)
        add('credentials', help='ETH DNS API Credentials INI file.')

    def more_info(self):
        return 'This plugin configures a DNS TXT record to respond to a ' + \
                'dns-01 challenge using the ETH DNS API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'ETH DNS API Credentials Ini file',
            {
                'host': 'Hostname and port of the API (e.g. my_api.com:5432)',
                'ca': 'PEM file path of the CA',
                'cert': 'PEM file path of the client certificate',
                'key': 'PEM file path of the client private key',
            }
        )

    def _perform(self, domain, validation_domain, validation_content):
        split = validation_domain.split('.', 1)
        request = api.CreateTxtRecordRequest()
        request.options = api.RecordOptions()
        request.value = validation_content
        request.txtName = split[0]
        request.subdomain = split[1]
        request.options.externallyViewable = True
        request.options.ttl = 60

        logger.debug("Create TXT record for {}".format(validation_domain))

        try:
            self._generate_client().CreateTxtRecord(request)
        except grpc.RpcError as e:
            code = e.code()
            if code == grpc.StatusCode.NOT_FOUND:
                logger.error("Unexpected")
            if code == grpc.StatusCode.INVALID_ARGUMENT:
                logger.error("I failed passing valid arguments. value: '{}', txtName: '{}', subdomain: '{}'".format(request.value, request.txtName, request.subdomain))
            log_common_errors(code)


    def _cleanup(self, domain, validation_domain, validation_content):
        request = api.DeleteTxtRecordRequest()
        request.value = validation_content
        request.fqName = validation_domain

        logger.debug("Delete TXT record for {}".format(validation_domain))

        try:
            self._generate_client().DeleteTxtRecord(request)
        except grpc.RpcError as e:
            code = e.code()
            if code == grpc.StatusCode.NOT_FOUND:
                logger.error("Tried to delete absent record")
            if code == grpc.StatusCode.INVALID_ARGUMENT:
                logger.error("I failed passing valid arguments. value: '{}', fqName: '{}'".format(request.value, request.fqName))
            log_common_errors(code)

    def _generate_client(self):
        ca = self.credentials.conf('ca')
        cert = self.credentials.conf('cert')
        key = self.credentials.conf('key')
        with open(ca, 'rb') as cafile, \
             open(cert, 'rb') as certfile, \
             open(key, 'rb') as keyfile:

            creds = grpc.ssl_channel_credentials(cafile.read(), keyfile.read(), certfile.read())
            channel = grpc.secure_channel(self.credentials.conf('host'), creds)
            return api_grpc.DnsStub(channel)


def log_common_errors(e):
    if e == grpc.StatusCode.INTERNAL:
        logger.error("DNS API had a problem")
    if e == grpc.StatusCode.UNAVAILABLE:
        logger.error("DNS API is down")
