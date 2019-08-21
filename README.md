# certbot-dns-eth-api

Certbot plugin for gRPC ETH DNS API

## Configuration

Have a INI configuration file with the API endpoint:

```ini
certbot_dns_eth_api:dns_eth_api_host = api.ethz.ch:50051
```

## Running

Generate a certificate with

```bash
certbot certonly                                                        \
        -a certbot-dns-eth-api:dns-eth-api                              \
        --certbot-dns-eth-api:dns-eth-api-credentials <CONFIG FILE>     \
        -d <DOMAIN>
```

to have it generate a certificate. `-d` can be specified multiple times.

