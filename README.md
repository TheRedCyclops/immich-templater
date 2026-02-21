# Immich configuration templater
This python script takes a base configuration from a configMap and fills it in with values from a secret for the smtp credentials and oidc credentials, storing the result back in a new "immich-config" secret
in deploy.yml there is an example on how to deploy this script
