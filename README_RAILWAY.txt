ZALP WEB COMMAND CENTER v2.1 - ACCOUNTS

Upload every file in this folder to the ROOT of the existing GitHub repository.

Features:
- Registration and login with username + password
- Passwords are stored as PBKDF2 hashes, not plaintext
- HttpOnly/SameSite session cookie, Secure on Railway HTTPS
- Separate project/speaker data per account
- Cookie notice; this app only uses the necessary login session cookie and has no analytics/ad cookies

IMPORTANT - PERSISTENT STORAGE:
In Railway, add a Volume to this service and mount it at:
  /app/zalp_web_data
The SQLite account database is stored at:
  /app/zalp_web_data/zalp_accounts.sqlite3
Without a persistent volume, user accounts and saved data may be lost when Railway replaces the container.

Each new account starts with its own default ZALP HOME EDITION project.
The old shared/anonymous database is not automatically copied to an account.

Use a unique password; do not reuse a password from another site.
