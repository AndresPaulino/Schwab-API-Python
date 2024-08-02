from flask import Flask, request, jsonify
from flask_cors import CORS
from schwabdev.api import Client
import os
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
app.logger.setLevel(logging.DEBUG)

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
    state = request.json.get('state')
    
    if not all([app_key, callback_url, state]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    auth_url = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri={callback_url}&state={state}'
    return jsonify({'authUrl': auth_url})

@app.route('/exchange-code', methods=['POST'])
def exchange_code():
    app.logger.info("Received request to exchange code")
    app.logger.debug(f"Request data: {request.json}")
    
    app_key = request.json.get('app_key')
    app_secret = request.json.get('app_secret')
    callback_url = request.json.get('callback_url')
    code = request.json.get('code')
    
    if not all([app_key, app_secret, callback_url, code]):
        app.logger.error("Missing required parameters")
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        client = Client(app_key, app_secret, callback_url=callback_url)
        response = client._post_oauth_token('authorization_code', code)
        app.logger.info(f"Schwab API response status: {response.status_code}")
        app.logger.debug(f"Schwab API response: {response.text}")
        
        if response.ok:
            tokens = response.json()
            return jsonify(tokens)
        else:
            app.logger.error(f"Failed to exchange code. Schwab API response: {response.text}")
            return jsonify({'error': 'Failed to exchange code', 'details': response.text}), response.status_code
    except Exception as e:
        app.logger.exception("Error exchanging code")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/account-details', methods=['GET'])
def get_account_details():
    app_key = request.headers.get('App-Key')
    app_secret = request.headers.get('App-Secret')
    access_token = request.headers.get('Access-Token')
    callback_url = request.headers.get('Callback-Url')
    
    if not all([app_key, app_secret, access_token, callback_url]):
        return jsonify({'error': 'Missing required headers'}), 400
    
    client = Client(app_key, app_secret, callback_url=callback_url)
    client.access_token = access_token
    details = client.account_details_all().json()
    return jsonify(details)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6060))
    app.run(host='0.0.0.0', port=port)