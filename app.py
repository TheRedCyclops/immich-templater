#!/usr/bin/env python3
import json
import os
from kubernetes import client, config, utils

# Initialize Kubernetes API

# Open ConfigMap
with open('base_config.json') as base_config:
    base_decoded = json.load(base_config)

# Open Secret(s)
def load_secrets():
    secret = api.read_namespaced_secret(name="immich-oidc-creds", namespace="immich")
# Insert Values
def template(base, secrets):
    # SMTP
    base['notifications']['smtp']['from'] = "Immich <smtp_username>"
    base['notifications']['smtp']['transport']['username'] = "smtp_username"
    base['notifications']['smtp']['transport']['password'] = "smtp_password"
    
    # OIDC
    base['oauth']['clientId'] = "client_id"
    base['oauth']['clientSecret'] = "client_secret"
    return base

def create_secret(string_data):
    body = client.V1Secret(
        api_version = "v1",
        string_data = string_data,
        kind = "Secret",
        metadata = client.V1ObjectMeta(
            name = "immich-config",
            namespace = "immich",
        )
    )
    api.create_namespaced_secret(namespace=immich, body=body)
def main():
    config.load_incluster_config()
    api = client.CoreV1Api()
    base = load_configmap(configMap)
    secrets = load_secrets('smtp_secret', 'oidc_secrets')
    filled_config = json.dump(template(base=base, secrets=secrets))
    create_secret(string_data={'config.json': filled_config})