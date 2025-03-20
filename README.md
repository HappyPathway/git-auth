# Generate GitHub Auth Token Action

This GitHub Action generates an authentication token for a GitHub App installation, which can be used to interact with GitHub APIs with the permissions granted to the GitHub App. It automatically handles token generation, expiration, and server time synchronization.

## What it Does

The action:
1. Creates a JWT (JSON Web Token) signed with your GitHub App's private key
2. Uses this JWT to authenticate and request an installation access token from the GitHub API
3. Outputs this token for use in subsequent steps of your workflow

## Features

- Automatic server time synchronization detection
- Handles token expiration with configurable duration
- Works with GitHub Enterprise Server
- Supports custom GitHub App configurations
- Detailed debug output for troubleshooting

## Prerequisites

- A GitHub App installed on your repository/organization
- The GitHub App's private key (PEM format)
- The installation ID of your GitHub App
- The GitHub App ID (optional, defaults to '6')

## Inputs

| Input | Description | Required | Default |
|-------|-------------|---------|---------|
| `github_app_pem_file` | The private key of your GitHub App in PEM format | Yes | N/A |
| `github_app_installation_id` | The installation ID of your GitHub App | Yes | N/A |
| `github_app_id` | The ID of your GitHub App | No | '6' |

## Outputs

| Output | Description |
|--------|-------------|
| `github_token` | The generated installation access token that can be used for GitHub API calls |

## Example Usage

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate GitHub Token
        id: auth
        uses: ./gh-auth
        with:
          github_app_pem_file: ${{ secrets.GITHUB_APP_PRIVATE_KEY }}
          github_app_installation_id: ${{ secrets.GITHUB_APP_INSTALLATION_ID }}
          github_app_id: '42'  # Optional, defaults to '6'
      
      - name: Use the token
        run: |
          # The token is available as:
          echo "Token: ${{ steps.auth.outputs.github_token }}"
          
          # Example API call using the token
          curl -H "Authorization: token ${{ steps.auth.outputs.github_token }}" \
               -H "Accept: application/vnd.github+json" \
               "$GITHUB_SERVER_URL/api/v3/repos/owner/repo/contents"
```

## Technical Details

### JWT Token Generation

The action generates a JWT token with the following characteristics:
- Algorithm: RS256
- Token lifetime: 9 minutes (to account for potential time drift)
- Claims:
  - `iat`: Issue time (current time)
  - `exp`: Expiration time
  - `iss`: Issuer (GitHub App ID)

### Time Synchronization

The action includes built-in time synchronization verification:
- Checks server time against local time
- Issues warnings if time difference exceeds 30 seconds
- Automatically adjusts token expiration to account for time differences

### Error Handling

The action includes comprehensive error handling for:
- Invalid private keys
- Network connectivity issues
- Server time synchronization problems
- Authentication failures
- API rate limiting

## How It Works

This action uses a Python script (`encode_jwt.py`) to:

1. Create a JWT token signed with your GitHub App's private key
2. Use the JWT to authenticate with GitHub API
3. Request an installation access token for the specified installation ID
4. Return this token for use in your workflow

The token generated typically:
- Has the permissions configured for your GitHub App installation
- Is valid for 60 minutes (after which a new token would need to be generated)
- Can be used with GitHub API endpoints by adding it to the Authorization header

## Dependencies

The script requires the following Python packages:
- cryptography
- requests

## Troubleshooting

If you encounter issues:

1. **404 Not Found errors**: Make sure the `github_app_installation_id` is correct and corresponds to an installation of your GitHub App
2. **Authentication errors**: Verify your GitHub App private key is valid
3. **App ID issues**: If you're not using the default App ID, make sure to provide the correct `github_app_id`
4. **Time synchronization errors**: Check for significant time differences between your runner and GitHub server
5. **SSL/TLS errors**: Ensure proper CA certificates are available (export REQUESTS_CA_BUNDLE if needed)

## Debug Mode

The action outputs detailed debug information when running, including:
- Server time synchronization status
- Token generation timestamps
- API request URLs and responses (excluding sensitive data)

## Security Notes

- The GitHub App private key is sensitive. Always store it as a secret.
- The generated token has the same permissions as your GitHub App installation.
- Minimize the permissions granted to your GitHub App to follow the principle of least privilege.
- Token expiration is set to 9 minutes by default to prevent token reuse and account for time drift.
- All API communications use HTTPS with proper certificate validation.

## Contributing

When contributing to this action:
1. Ensure all security measures remain intact
2. Test with both GitHub Enterprise Server and github.com
3. Verify time synchronization handling
4. Maintain backward compatibility with existing installations
5. Update documentation for any new features or changes
