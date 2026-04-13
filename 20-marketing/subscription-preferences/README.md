# Subscription Preferences

Owns communication preferences and subscription-status operations.

## Power

- Read a contact's subscription status.
- Batch read or batch update contact subscription statuses.
- Subscribe or unsubscribe contacts where policy allows.

## Common Calls

- `GET /communication-preferences/v3/status/email/{emailAddress}`
- `POST /communication-preferences/v3/statuses/batch/read`
- `POST /communication-preferences/v3/statuses/batch/write`

