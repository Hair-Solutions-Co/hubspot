# Files

Owns File Manager and file download/upload surfaces.

## Power

- Upload files.
- Import files from URL.
- Search files and fetch metadata.
- Download user files or hidden/system files when granted `files.ui_hidden.read`.

## Common Calls

- `GET /files/v3/files`
- `GET /files/v3/files/{fileId}`
- `POST /files/v3/files`
- `POST /files/v3/files/import-from-url/async`
- `POST /files/v3/files/search`
- `DELETE /files/v3/files/{fileId}`

