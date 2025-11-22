Auth model (current):
- Bearer token stored at /var/lib/polyflow/api_token (create if missing).
- ENV overrides:
  - ROBOT_API_TOKEN_PATH: token file path.
  - ROBOT_API_ALLOWED_ORIGINS: comma-separated list for CORS (optional; if empty, CORS disabled).
- Health endpoint is unauthenticated; all others require Authorization: Bearer <token>.
- Token is plain text; you can rotate by replacing the file and restarting the service.
