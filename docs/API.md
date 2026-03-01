# API Details

## Create Project
`POST /api/v1/projects`

Form-data:
- `name: string`
- `audio: wav|mp3`

Response:
```json
{ "project_id": 1, "status": "queued" }
```

## Project Status
`GET /api/v1/projects/{project_id}/status`

## Get Tab
`GET /api/v1/projects/{project_id}/tab`

Response includes tuning, tempo, mapped notes, and rendered ASCII tab.

## Exports
`POST /api/v1/projects/{project_id}/export/midi`

`POST /api/v1/projects/{project_id}/export/gp5`
