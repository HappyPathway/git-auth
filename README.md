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

## GitHub App Setup

### 1. Create a GitHub App
1. Go to your GitHub Enterprise Server Organization Settings
2. Navigate to `Developer Settings` > `GitHub Apps` > `New GitHub App`
3. Fill in the required information:
   - **GitHub App Name**: Choose a descriptive name (e.g., "Terraform Automation App")
   - **Homepage URL**: Your organization's URL or repository URL
   - **Webhook**: Disable webhook (uncheck "Active")
   
### 2. Set Permissions
Configure the following permissions based on your needs:
- **Repository Permissions**:
  - Contents: Read & write
  - Metadata: Read-only
  - Pull requests: Read & write (if needed)
  - Workflows: Read & write (if needed)
- **Organization Permissions**:
  - Members: Read-only
  - Projects: Read-only

### 3. Generate Private Key
1. After creating the app, scroll to the "Private keys" section
2. Click "Generate a private key"
3. Save the downloaded .pem file securely
4. Convert the key to a single line format if needed:
   ```bash
   awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' your-private-key.pem
   ```

### 4. Install the App
1. Navigate to the "Install App" tab
2. Choose the organization where you want to install the app
3. Select the repositories you want the app to access
4. Complete the installation

### 5. Gather Required Information
You'll need these values for the action:
1. **App ID**: Found on the app's settings page
2. **Installation ID**: Found in the URL when viewing the app's installation
   (e.g., `.../github-apps/your-app/installations/123` - here 123 is the installation ID)
3. **Private Key**: The .pem file you downloaded

### 6. Configure Action Secrets
Add the following secrets to your GitHub repository or organization:
1. `GITHUB_APP_PRIVATE_KEY`: The contents of your .pem file
2. `GITHUB_APP_INSTALLATION_ID`: The installation ID from step 5
3. (Optional) `GITHUB_APP_ID`: The App ID from step 5 if different from default '6'

### Security Best Practices
1. Generate a new private key if the existing one is compromised
2. Regularly rotate private keys (recommended every 60-90 days)
3. Grant only the minimum required permissions
4. Restrict app installation to specific repositories
5. Monitor app activity in organization audit logs

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
6. **Installation errors**:
   - Verify the app is properly installed on the target repository
   - Check if the installation ID matches the repository's installation
   - Ensure the private key hasn't expired
   - Confirm the app has the required permissions

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
