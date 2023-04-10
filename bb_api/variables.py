import os

from dotenv import load_dotenv
load_dotenv()

application_key_id = os.getenv('BB_ID')
application_key = os.getenv('BB_KEY')

api_url = os.getenv('BB_API_URL')
account_authorization_token = os.getenv('BB_AUTH_TOKEN')
bucket_id = os.getenv('BB_BUCKET_ID')

upload_url = os.getenv('BB_UPLOAD_URL')
upload_authorization_token = os.getenv('BB_UPLOAD_AUTH_TOKEN')

bucket_name = os.getenv('BB_BUCKET_NAME')
bucket_download_url = os.getenv('BB_DOWNLOAD_URL')