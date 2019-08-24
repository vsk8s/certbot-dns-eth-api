#!/usr/bin/env python3
import os
import re
import shutil

from setuptools import setup, Command
from setuptools import find_packages
from setuptools.command.build_py import build_py

install_requires = [
    'acme>=0.29.0',
    'certbot>=0.34.0',
    'setuptools',
    'zope.interface',
    'grpcio',
    'grpcio-tools',
]


# See https://stackoverflow.com/a/54236739/3589716
class GrpcTool (Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import grpc_tools.protoc

        cwd = os.getcwd()
        os.chdir(cwd + '/proto')

        grpc_tools.protoc.main([
            'grpc_tools.protoc',
            '--python_out=../certbot_dns_eth_api',
            '--grpc_python_out=../certbot_dns_eth_api',
            'dnsapi.proto'
        ])

        os.chdir(cwd)
        with open('certbot_dns_eth_api/dnsapi_pb2_grpc.py', 'r+') as file:
            data = file.read()
            file.seek(0)
            file.write(re.sub("import dnsapi_pb2", "import certbot_dns_eth_api.dnsapi_pb2", data))
            file.truncate()


class BuildPyCommand (build_py):
    def run(self):
        self.run_command('grpc')
        super(BuildPyCommand, self).run()

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
    cmdclass = {
      "build_py": BuildPyCommand,
      "grpc": GrpcTool,
    },
)


