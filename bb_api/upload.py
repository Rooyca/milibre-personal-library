import json, requests, hashlib, mimetypes

from .variables import *

def upload_this_file(file, file_name):

    with open(file, 'rb') as f:
        file_data = f.read()

    try:
        content_type = mimetypes.guess_type(file_data)
        print(content_type)
    except:
        content_type = 'b2/x-auto'

    sha1_of_file_data = hashlib.sha1(file_data).hexdigest()

    headers = {
        'Authorization' : upload_authorization_token,
        'X-Bz-File-Name' :  file_name,
        'Content-Type' : content_type,
        'X-Bz-Content-Sha1' : sha1_of_file_data,
        # Author Name
        'X-Bz-Info-Author' : 'rooyca'
        #'X-Bz-Server-Side-Encryption' : 'AES256'
        }
    request = requests.post(upload_url, data=file_data, headers=headers)

    response_data = json.loads(request.text)
    
    return bucket_download_url + '/file/' + bucket_name + '/' + response_data['fileName']