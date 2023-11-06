import os
import msal
import logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

def get_id_token():
    tenant_id = os.getenv('AZURE_TENANT_ID')
    resource_id = os.getenv('AZURE_AD_APP_RESOURCE_ID')
    client_id = os.getenv('INTEGRATION_TESTER')
    client_secret = os.getenv('AZURE_TESTER_SERVICEPRINCIPAL_SECRET')

    authority_host_uri = 'https://login.microsoftonline.com'
    authority_uri = authority_host_uri + '/' + tenant_id
    scopes = [resource_id + '/.default']

    try:
        app = msal.ConfidentialClientApplication(client_id=client_id, authority=authority_uri, client_credential=client_secret)
        result = app.acquire_token_for_client(scopes=scopes)
        print(result.get('access_token'))
        return result.get('access_token')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    get_id_token()