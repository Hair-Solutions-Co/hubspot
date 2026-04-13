# Forms

Owns HubSpot form definitions and submission-facing integration surfaces.

## Power

- Read, create, clone, rename, and delete forms.
- Submit form data from external systems.
- Retrieve uploaded files submitted through forms when granted.

## Common Calls

- `GET /marketing/v3/forms`
- `GET /marketing/v3/forms/{formId}`
- `POST /marketing/v3/forms`
- `PATCH /marketing/v3/forms/{formId}`
- `DELETE /marketing/v3/forms/{formId}`
- `POST /submissions/v3/integration/submit/{portalId}/{formGuid}`

