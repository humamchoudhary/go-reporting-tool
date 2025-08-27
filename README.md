# API Documentation

## Overview

This API provides a natural language interface to generate reports from a MySQL database. It uses Google's Gemini AI to interpret natural language queries, generate SQL, execute them, and provide both raw data and textual interpretations.

## Authentication

All endpoints require API key authentication via:

- Header: `X-API-KEY: your-public-key`

## Endpoints

### 1. Generate Report

**Endpoint:** `GET /generate-report`

Generates a report based on a natural language prompt by:

1. Converting the prompt to a SQL query using Gemini
2. Executing the query against the MySQL database
3. Interpreting the results using Gemini
4. Returning both the interpreted text and raw data

**Request Body (JSON):**

```json
{
  "prompt": "string (required)",
  "sys_prompt": "string (optional)"
}
```

**Parameters:**

- `prompt`: Natural language query (e.g., "what is all the pending tasks for Humam") [required]
- `sys_prompt`: context for the interpretation phase [required]

**Response:**

```json
{
  "status": "string",
  "message": "string",
  "data": {
    "text": "string (markdown)",
    "raw_data": "json array"
  }
}
```

**Response Fields:**

- `status`: Either "success" or "error"
- `message`: Human-readable status message
- `data.text`: **Markdown-formatted text** containing the AI-generated interpretation of the results. This should be rendered by a markdown renderer for proper display.
- `data.raw_data`: JSON array containing the raw database results

**Example Request:**

```bash
curl -X GET \\
  -H "Content-Type: application/json" \\
  -H "X-API-KEY: your-public-key" \\
  -d '{"prompt": "what is all the pending tasks for Humam"}' \\
  <ip_addr/generate-report>

```

**Example Response:**

```json
{
  "status": "success",
  "message": "Report generated successfully",
  "data": {
    "text": "## Pending Tasks for Team Members Named Humam\\n\\nThere are **3 pending tasks** assigned to team members with 'Humam' in their name:\\n\\n- **Humam Ahmed**: 'Design Homepage' (Due: April 15, 2024)\\n- **Humam Khan**: 'Write documentation' (Due: April 25, 2024)\\n- **Humam XYZ**: 'Social media campaign' (Due: April 30, 2024)\\n\\nAll tasks are currently pending and should be prioritized based on their due dates.",
    "raw_data": [
      {
        "task_id": "T-101",
        "task_name": "Design Homepage",
        "assigned_to": "Humam Ahmed",
        "status": "Pending",
        "due_date": "2024-04-15"
      },
      {
        "task_id": "T-104",
        "task_name": "Write documentation",
        "assigned_to": "Humam Khan",
        "status": "Pending",
        "due_date": "2024-04-25"
      },
      {
        "task_id": "T-106",
        "task_name": "Social media campaign",
        "assigned_to": "Humam XYZ",
        "status": "Pending",
        "due_date": "2024-04-30"
      }
    ]
  }
}
```

### 2. Health Check

**Endpoint:** `GET /health`

Checks if the API is running properly.

**Response:**

```json
{
  "status": "string",
  "message": "string",
  "data": null
}
```

**Example Request:**

```bash
curl -X GET <ip_addr/health>

```

**Example Response:**

```json
{
  "status": "success",
  "message": "API is running successfully",
  "data": null
}
```

## Error Responses

The API returns standardized error responses with appropriate HTTP status codes:

**Authentication Error (401):**

```json
{
  "status": "error",
  "message": "Invalid or missing API key"
}
```

**Bad Request (400):**

```json
{
  "status": "error",
  "message": "Missing 'prompt' in request body"
}
```

**Server Error (500):**

```json
{
  "status": "error",
  "message": "Detailed error description"
}
```

## Database Schema

The API works with the following tables:

1. **tasks**: Task management information
2. **leads**: Sales lead information
3. **projects**: Project details
4. **timesheets**: Time tracking data

## Server Setup Setup Requirements

1. Set environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `PUBLIC_KEY`: Your API authentication key
   - MySQL connection details: `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage Notes

- The `text` field in responses contains markdown-formatted content that should be rendered using a markdown renderer
- The `raw_data` field contains the exact JSON results from the database query
- For name searches, the API uses fuzzy matching (LIKE '%name%') to handle variations
