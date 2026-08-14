# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

**DO NOT open a public issue for security vulnerabilities.**

### How to Report

1. **GitHub Private Vulnerability Reporting** (Preferred)
   - Go to the Security tab
   - Click "Report a vulnerability"
   - Fill in the details

2. **Email** (If configured)
   - Send to: [SECURITY_EMAIL_PLACEHOLDER]
   - Include: Description, steps to reproduce, impact

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix or mitigation:** Depends on severity

## Security Considerations

### API Keys and Secrets

- Never commit API keys to version control
- Use environment variables for secrets
- Use `.env` files for local development (never commit)
- Rotate keys if accidentally exposed

### Provider Security

- All provider API keys are stored in environment variables
- Keys are never logged or exported
- Keys are never shown in CLI output
- Doctor command reports status without revealing keys

### External Content

LeedHunter processes external content from web searches. This content is treated as **untrusted data**:

- Web pages may contain prompt injection attempts
- External content is never treated as instructions
- All LLM output is schema-validated
- External content cannot modify system behavior

### Database Security

- Use strong passwords for PostgreSQL
- Don't expose database to public internet
- Use connection pooling
- Enable SSL for remote connections

### Network Security

- Use HTTPS for all API calls
- Validate SSL certificates
- Implement timeouts
- Handle rate limits gracefully

## Privacy

### Data Collection

LeedHunter collects:
- Business names, domains, contact information (from public sources)
- Search queries and results
- Research metadata

LeedHunter does NOT collect:
- User personal information
- Authentication credentials
- Private communications

### Data Storage

- Research data is stored locally in PostgreSQL
- No data is sent to third parties (except search providers)
- Users control their own data

### Data Retention

- Users can export their data
- Users can delete their data
- No automatic data sharing

## Provider Terms of Service

Users are responsible for complying with provider terms of service:
- [Tavily Terms](https://tavily.com/terms)
- [Brave Search Terms](https://brave.com/search/api/tos/)
- [Anthropic Terms](https://www.anthropic.com/policies/terms)
- [OpenAI Terms](https://openai.com/policies/terms-of-use)

## Best Practices

1. **Keep dependencies updated**
2. **Run security audits regularly**
3. **Use strong, unique API keys**
4. **Monitor for unusual activity**
5. **Back up your data**
6. **Use a dedicated database user with minimal privileges**

## Contact

For security concerns, use GitHub's private vulnerability reporting.
