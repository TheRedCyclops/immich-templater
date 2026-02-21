#!/usr/bin/env python3
import json
import os
import base64
from kubernetes.client.rest import ApiException
from kubernetes import client, config, utils

# Get Namespace for Namespace awareness
try:
    with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace', r) as namespace:
        namespace = namespace 
except:
    namespace = "immich"
    print("Failed to get namespace, using default %s" namespace)
# Open ConfigMap
def load_config_map(name):
    try:
        config_map_data = api.read_namespaced_config_map(name=name, namespace=namespace).data
    except ApiException as e:
        print("Error getting configMap %s: %s" % (name, e))
    return config_map_data
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
def template(base, smtp_secret, oidc_secret):
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
    try:
        api.create_namespaced_secret(namespace=namespace, body=body)
    except ApiException as e:
        print("Error creating secret: %s" % e)
def main():
    config.load_incluster_config()
    api = client.CoreV1Api()
    base = load_config_map(os.environ['CONFIG_BASE'])
    smtp_secret = load_secret(os.environ['SMTP_CREDENTIALS_SECRET'])
    oidc_secret = load_secret(os.environ['OIDC_CREDENTIALS_SECRET'])
    filled_config = json.dump(template(base=base, smtp_secret=smtp_secret, oidc_secret=oidc_secret))
    create_secret(string_data={'config.json': filled_config})