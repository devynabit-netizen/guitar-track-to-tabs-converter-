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

Response fields:
- `status`: `queued | processing | complete | failed`
- `progress`: `0.0 - 1.0`
- `current_phase`: current phase number (`1-5`)
- `total_phases`: fixed at `5`
- `phase_name`: `uploaded | preprocessing | transcribing | tab_generation | finalizing`
- `error_message`: present when status is `failed`
- `error_code`: machine-readable failure type when status is `failed`

## Get Tab
`GET /api/v1/projects/{project_id}/tab`

Response includes tuning, tempo, mapped notes, and rendered ASCII tab.

## Exports
`POST /api/v1/projects/{project_id}/export/midi`

`POST /api/v1/projects/{project_id}/export/gp5`
