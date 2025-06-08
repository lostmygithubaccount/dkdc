- follow 12factor best practices
- update `dkdc.config` to basically load in a `.env` (from ~/.dkdc/.env` and ~/.env), loading in a way that makes sense)
- replace config (esp for postgres and such) used across Python and Bash as environment variables
- write .env locally w/ these setup to the same as they are now
- use no external dependnecies for this config stuff, just Python

