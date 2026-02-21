#!/usr/bin/env python3
import json
import os
import base64
from kubernetes.client.rest import ApiException
import kubernetes.client
from kubernetes import client, config, utils

# Get Namespace for Namespace awareness
def get_namespace():
    try:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace', r) as namespace:
            namespace = namespace 
    except:
        namespace = "immich"
        print("Failed to get namespace, using default %s" % namespace)
    return namespace
# Open ConfigMap
def load_config_map(name):
    try:
        config_map_json = api.read_namespaced_config_map(name=name, namespace=namespace).data['config.json']
        config_map_data = json.loads(config_map_json)
    except ApiException as e:
        print("Error getting configMap %s: %s" % (name, e))
    return config_map_data
# Open Secret(s)
def load_secret(name):
    try:
        secret_data = api.read_namespaced_secret(name=name, namespace=namespace).data
    except ApiException as e:
        print("Error getting secret %s: %s" % (name, e))
    decoded_data = {}
    for entry in secret_data:
        decoded_data[entry] = base64.b64decode(secret_data[entry])
    return decoded_data

# Insert Values
def template(base, smtp_secret, oidc_secret):
    # SMTP
    base['notifications']['smtp']['from'] = "Immich <{}>".format(str(smtp_secret['username']).decode("utf-8"))
    base['notifications']['smtp']['transport']['username'] = str(smtp_secret['username']).decode("utf-8")
    base['notifications']['smtp']['transport']['password'] = str(smtp_secret['password']).decode("utf-8")
    
    # OIDC
    base['oauth']['clientId'] = str(oidc_secret["client_id"]).decode("utf-8")
    base['oauth']['clientSecret'] = str(oidc_secret["client_secret"]).decode("utf-8")
    return base

def create_secret(string_data):
    body = client.V1Secret(
        api_version = "v1",
        string_data = string_data,
        kind = "Secret",
        metadata = client.V1ObjectMeta(
            name = "immich-immich-config",
            namespace = namespace,
        )
    )
    try:
        api.create_namespaced_secret(namespace=namespace, body=body)
    except ApiException as e:
        print("Error creating secret: %s" % e)

config.load_incluster_config()
api = client.CoreV1Api()
namespace = get_namespace()
def main():
    print("Loading base config")
    base = load_config_map(os.environ['CONFIG_BASE'])
    print("Loading secrets")
    smtp_secret = load_secret(os.environ['SMTP_CREDENTIALS_SECRET'])
    oidc_secret = load_secret(os.environ['OIDC_CREDENTIALS_SECRET'])
    filled_config = json.dumps(template(base=base, smtp_secret=smtp_secret, oidc_secret=oidc_secret))
    print("Creating secret")
    create_secret(string_data={'config.json': filled_config})

if __name__ == '__main__':
  main()