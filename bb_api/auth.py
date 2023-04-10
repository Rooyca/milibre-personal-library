
import requests, json, os, base64

from dotenv import load_dotenv, set_key
load_dotenv()

application_key_id = os.getenv('BB_ID')
application_key = os.getenv('BB_KEY')
bucket_id = os.getenv('BB_BUCKET_ID')

def get_variables_auth():

    id_and_key = f'{application_key_id}:{application_key}'
    basic_auth_string = 'Basic ' + str(base64.b64encode(id_and_key.encode()).decode())

    headers = { 'Authorization': basic_auth_string }

    response = requests.get(
        'https://api.backblazeb2.com/b2api/v2/b2_authorize_account',
        headers = headers
        )

    response_data = json.loads(response.text)

    set_key(".env", "BB_AUTH_TOKEN", response_data['authorizationToken'])
    set_key(".env", "BB_API_URL", response_data['apiUrl'])
    set_key(".env", "BB_DOWNLOAD_URL", response_data['downloadUrl'])

    account_authorization_token = response_data['authorizationToken']
    api_url = response_data['apiUrl']

    request = requests.post(api_url + '/b2api/v2/b2_get_upload_url',
                            json = { 'bucketId' : bucket_id }, 
                            headers = { 'Authorization': account_authorization_token })

    response_data = json.loads(request.text)

    set_key(".env", "BB_UPLOAD_URL", response_data['uploadUrl'])
    set_key(".env", "BB_UPLOAD_AUTH_TOKEN", response_data['authorizationToken'])

    print('Variables updated successfully!')