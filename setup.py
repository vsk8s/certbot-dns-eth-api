from setuptools import setup
from setuptools import find_packages

install_requires = [
    'acme>=0.29.0',
    'certbot>=0.34.0',
    'setuptools',
    'zope.interface',
    'grpcio',
]

setup(
    name = 'certbot-dns-eth-api',
    version = '0.1.0',
    description = 'ETH DNS API Authenticator plugin for Certbot',
    url = 'https://git.sos.ethz.ch/k8s/certbot-dns-eth-api',
    entry_points = {
        'certbot.plugins': [
            'dns-eth-api = certbot_dns_eth_api.dns_eth:Authenticator',
        ],
    },
    packages = find_packages(),
)


