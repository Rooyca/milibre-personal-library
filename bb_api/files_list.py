from .variables import *

request = requests.post(api_url + '/b2api/v2/b2_list_file_names', 
                        json = { 'bucketId' : bucket_id }, 
                        headers = { 'Authorization': account_authorization_token })


response_data = json.loads(request.text)
print(json.dumps(response_data, indent=4))