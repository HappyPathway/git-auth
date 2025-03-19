# Generate GitHub Auth Token Action

This GitHub Action generates an authentication token for a GitHub App installation, which can be used to interact with GitHub APIs with the permissions granted to the GitHub App.

## What it Does

The action:
1. Creates a JWT (JSON Web Token) signed with your GitHub App's private key
2. Uses this JWT to authenticate and request an installation access token from the GitHub API
3. Outputs this token for use in subsequent steps of your workflow

## Inputs

| Input | Description | Required | Default |
|-------|-------------|---------|---------|
| `github_app_pem_file` | The private key of your GitHub App in PEM format | Yes | N/A |
| `github_app_installation_id` | The installation ID of your GitHub App | Yes | N/A |
| `github_base_url` | The base URL of your GitHub instance (e.g., https://github.com for GitHub.com or https://github.e.it.census.gov for GitHub Enterprise) | Yes | N/A |
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
          github_base_url: 'https://github.e.it.census.gov'
          github_app_id: '42'  # Optional, defaults to '6'
      
      - name: Use the token
        run: |
          # The token is available as:
          echo "Token: ${{ steps.auth.outputs.github_token }}"
          
          # Example API call using the token
          curl -H "Authorization: token ${{ steps.auth.outputs.github_token }}" \
               -H "Accept: application/vnd.github+json" \
               "https://github.e.it.census.gov/api/v3/repos/owner/repo/contents"
```

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

## Troubleshooting

If you encounter issues:

1. **404 Not Found errors**: Make sure the `github_app_installation_id` is correct and corresponds to an installation of your GitHub App
2. **Authentication errors**: Verify your GitHub App private key is valid
3. **App ID issues**: If you're not using the default App ID, make sure to provide the correct `github_app_id`
4. **URL format problems**: Ensure your GitHub base URL is correct (e.g., includes protocol, no trailing slash)

## Security Notes

- The GitHub App private key is sensitive. Always store it as a secret.
- The generated token has the same permissions as your GitHub App installation.
- Minimize the permissions granted to your GitHub App to follow the principle of least privilege.
