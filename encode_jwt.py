## Run this script set the private key as github_app_private_key and installation_id as the installation id of the app

#export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-bundle.crt
#export github_app_private_key="-----BEGIN"
#export github_app_installation_id=11
#export github_app_url=https://github.e.it.census.gov
#export GITHUB_TOKEN=$(python encode_jwt.py --private-key "$github_app_private_key" --installation-id "$github_app_installation_id" --enterprise-url "$github_app_url")

import time
import json
import base64
import argparse
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import sys

# Set up argument parser
parser = argparse.ArgumentParser(description='Encode JWT with RS256 and get GitHub Enterprise installation access token')
parser.add_argument('--private-key', '-k', type=str, required=True, help='PEM formatted private key string')
parser.add_argument('--installation-id', '-i', type=str, required=True, help='GitHub App Installation ID')
parser.add_argument('--enterprise-url', '-u', type=str, required=True, help='GitHub Enterprise API URL (e.g., https://github.e.it.census.gov)')
parser.add_argument('--app-id', '-a', type=str, default='6', help='GitHub App ID (default: 6)')
args = parser.parse_args()

# Ensure URL has proper formatting with trailing slash
enterprise_url = args.enterprise_url
if not enterprise_url.endswith('/'):
    enterprise_url += '/'

# Load the PEM private key
private_key = load_pem_private_key(args.private_key.encode(), password=None)

# JWT Header
header = {
    "alg": "RS256",
    "typ": "JWT"
}

# Before creating the JWT, check server time
meta_url = f"{enterprise_url}api/v3/meta"
try:
    meta_response = requests.get(meta_url)
    if 'date' in meta_response.headers:
        server_time = time.mktime(time.strptime(meta_response.headers['date'], '%a, %d %b %Y %H:%M:%S %Z'))
        time_diff = abs(server_time - time.time())
        print(f"Debug - Server time: {time.ctime(server_time)}", file=sys.stderr)
        print(f"Debug - Time difference with server: {time_diff:.2f} seconds", file=sys.stderr)
        if time_diff > 30:  # If time difference is more than 30 seconds
            print(f"Warning - Large time difference detected with server ({time_diff:.2f} seconds)", file=sys.stderr)
except Exception as e:
    print(f"Warning - Could not check server time: {str(e)}", file=sys.stderr)

# JWT Payload - using app_id for issuer, not installation_id
current_time = int(time.time())
expiration_time = current_time + (10 * 60)  # Back to 10 minutes
payload = {
    "iat": current_time,
    "exp": expiration_time,
    "iss": args.app_id
}

print(f"Debug - Current time: {time.ctime(current_time)}", file=sys.stderr)
print(f"Debug - Expiration time: {time.ctime(expiration_time)}", file=sys.stderr)

# Encode Header and Payload as Base64
header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

# Create the message (header + payload)
message = f"{header_encoded}.{payload_encoded}".encode()

# Sign the message using RS256
signature = private_key.sign(
    message,
    padding.PKCS1v15(),
    hashes.SHA256()
)

# Encode the signature in Base64
signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip("=")

# Construct the full JWT
jwt_token = f"{header_encoded}.{payload_encoded}.{signature_encoded}"

# Prepare the request to get the installation access token
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Accept": "application/vnd.github+json"
}

# Make the request to the GitHub Enterprise API to get the installation access token
url = f"{enterprise_url}api/v3/app/installations/{args.installation_id}/access_tokens"
print(f"Requesting token from: {url}", file=sys.stderr)
response = requests.post(url, headers=headers)

# Check if the request was successful
if response.status_code == 201:
    installation_access_token = response.json().get('token')
    print(installation_access_token)  # Output the token only
else:
    # Raise an error with a message
    sys.stderr.write(f"Error: Failed to get installation access token. Status code: {response.status_code}\n")
    sys.stderr.write(f"{response.text}\n")
    sys.exit(1)  # Exit with an error code
