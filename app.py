#!/usr/bin/env python3
import json
import os
import base64
from kubernetes.client.rest import ApiException
from kubernetes import client, config, utils

# Get Namespace for Namespace awareness
with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace', r) as namespace:
    namespace = namespace 

# Open ConfigMap
with open('base_config.json', r) as base_config:
    base_decoded = json.load(base_config)

# Open Secret(s)
def load_secret(name):
    try:
        secret_data = api.read_namespaced_secret(name=name, namespace=namespace).body.data()
    except ApiException as e:
        print("Error getting secret %s: %s" % (name, e))
    decoded_data = {}
    for entry in secret_data:
        decoded_data[entry] = base64.b64decode(secret_data[entry])
    return decoded_data

# Insert Values
def template(base, secrets):
    # SMTP
    base['notifications']['smtp']['from'] = "Immich <{}>".format(smtp_secret['username'])
    base['notifications']['smtp']['transport']['username'] = smtp_secret['username']
    base['notifications']['smtp']['transport']['password'] = smtp_secret['password']
    
    # OIDC
    base['oauth']['clientId'] = oidc_secret["client_id"]
    base['oauth']['clientSecret'] = oidc_secret["client_secret"]
    return base

def create_secret(string_data):
    body = client.V1Secret(
        api_version = "v1",
        string_data = string_data,
        kind = "Secret",
        metadata = client.V1ObjectMeta(
            name = "immich-config",
            namespace = namespace,
        )
    )
    api.create_namespaced_secret(namespace=namespace, body=body)
def main():
    config.load_incluster_config()
    api = client.CoreV1Api()
    base = load_configmap(configMap)
    smtp_secret = load_secret(os.environ['SMTP_CREDENTIALS_SECRET'])
    oidc_secret = load_secret(os.environ['OIDC_CREDENTIALS_SECRET'])
    filled_config = json.dump(template(base=base, secrets=secrets))
    create_secret(string_data={'config.json': filled_config})