from flask import Flask, request, jsonify
from schwabdev.api import Client
import os

app = Flask(__name__)

@app.route('/initialize', methods=['POST'])
def initialize_client():
    app_key = request.json.get('app_key')
    app_secret = request.json.get('app_secret')
    callback_url = request.json.get('callback_url')
    
    if not all([app_key, app_secret, callback_url]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    client = Client(app_key, app_secret, callback_url=callback_url)
    return jsonify({'message': 'Client initialized successfully'})

@app.route('/generate-auth-url', methods=['POST'])
def generate_auth_url():
    app_key = request.json.get('app_key')
    callback_url = request.json.get('callback_url')
    
    if not all([app_key, callback_url]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    auth_url = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri={callback_url}'
    return jsonify({'authUrl': auth_url})

@app.route('/exchange-code', methods=['POST'])
def exchange_code():
    app_key = request.json.get('app_key')
    app_secret = request.json.get('app_secret')
    callback_url = request.json.get('callback_url')
    code = request.json.get('code')
    
    if not all([app_key, app_secret, callback_url, code]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    client = Client(app_key, app_secret, callback_url=callback_url)
    response = client._post_oauth_token('authorization_code', code)
    if response.ok:
        tokens = response.json()
        return jsonify(tokens)
    else:
        return jsonify({'error': 'Failed to exchange code'}), 400

@app.route('/account-details', methods=['GET'])
def get_account_details():
    app_key = request.headers.get('App-Key')
    app_secret = request.headers.get('App-Secret')
    access_token = request.headers.get('Access-Token')
    
    if not all([app_key, app_secret, access_token]):
        return jsonify({'error': 'Missing required headers'}), 400
    
    client = Client(app_key, app_secret)
    client.access_token = access_token
    details = client.account_details_all().json()
    return jsonify(details)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)