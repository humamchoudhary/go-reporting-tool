from flask import Flask, request, jsonify
import mysql.connector
import google.generativeai as genai
import os
from functools import wraps
import logging

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['GEMINI_API_KEY'] = os.environ.get(
    'GEMINI_API_KEY', 'your-gemini-api-key-here')
app.config['PUBLIC_KEY'] = os.environ.get(
    'PUBLIC_KEY', 'your-public-key-here')  # For API authentication
app.config['MYSQL_CONFIG'] = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'reporting_db')
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini
genai.configure(api_key=app.config['GEMINI_API_KEY'])

# Database table schemas for the prompt
TABLE_SCHEMAS = """
Database Tables Schema:

1. tasks:
   - task_id (varchar): Unique identifier for the task
   - task_name (varchar): Name/description of the task
   - assigned_to (varchar): Name of the person the task is assigned to
   - status (varchar): Status of the task (e.g., 'Pending', 'In Progress', 'Completed')
   - due_date (date): Due date of the task
   - project_id (varchar): Reference to projects table

2. leads:
   - lead_id (varchar): Unique identifier for the lead
   - lead_name (varchar): Name of the lead
   - status (varchar): Status of the lead (e.g., 'New', 'Contacted', 'Qualified')
   - assigned_to (varchar): Name of the person the lead is assigned to
   - created_date (date): Date when the lead was created

3. projects:
   - project_id (varchar): Unique identifier for the project
   - project_name (varchar): Name of the project
   - status (varchar): Status of the project (e.g., 'Active', 'Completed', 'On Hold')
   - start_date (date): Start date of the project
   - end_date (date): End date of the project

4. timesheets:
   - timesheet_id (varchar): Unique identifier for the timesheet entry
   - employee_name (varchar): Name of the employee
   - task_id (varchar): Reference to tasks table
   - hours (decimal): Number of hours worked
   - date (date): Date of the timesheet entry
"""

# System prompt for SQL generation
SQL_GENERATION_PROMPT = f"""
You are a SQL query generator. Based on the user's natural language request, generate a MySQL query that answers their question.

{TABLE_SCHEMAS}

Important Instructions:
1. Only generate queries for the tables mentioned above (tasks, leads, projects, timesheets)
2. For name searches, use the LIKE operator with wildcards to handle variations (e.g., 'Humam', 'M humam', 'Humam xyz')
3. Return ONLY the SQL query without any additional explanation, formatting, or code blocks
4. Make sure the query is syntactically correct and efficient
5. Use appropriate WHERE clauses to filter based on the request
6. Select only the relevant columns needed to answer the question

Example:
Input: "what is all the pending tasks for Humam"
Output: "SELECT task_id, task_name, assigned_to, status, due_date FROM tasks WHERE status = 'Pending' AND assigned_to LIKE '%Humam%'"
"""

# System prompt for textual interpretation
TEXT_INTERPRETATION_PROMPT = """
You are a data analyst assistant. Your task is to interpret SQL query results and provide a clear, concise textual summary.

Guidelines:
1. Analyze the data and provide meaningful insights
2. Focus on the most important information
3. Use natural language that a business user would understand
4. Keep the response concise but informative
5. Highlight any notable patterns, trends, or outliers
6. If there are dates, provide context about timelines
7. If there are statuses, summarize the distribution
8. If the data is empty, explain what that means in context

Example:
Input data: [{"task_id": "T-101", "task_name": "Design Homepage", "assigned_to": "Humam Ahmed", "status": "Pending", "due_date": "2024-04-15"}]
Response: "There is 1 pending task assigned to Humam Ahmed: 'Design Homepage' which is due on April 15, 2024."
"""

# Helper functions for standardized responses


def success_response(data=None, message="Operation completed successfully"):
    response = {
        "status": "success",
        "message": message,
        "data": data
    }
    return jsonify(response)


def error_response(message="An error occurred", status_code=400):
    response = {
        "status": "error",
        "message": message
    }
    return jsonify(response), status_code

# Authentication decorator


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get(
            'X-API-KEY')
        if not provided_key or provided_key != app.config['PUBLIC_KEY']:
            return error_response("Invalid or missing API key", 401)
        return f(*args, **kwargs)
    return decorated_function

# Function to generate SQL query using Gemini


def generate_sql_query(natural_language_query):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        full_prompt = f"{SQL_GENERATION_PROMPT}\n\nInput: {
            natural_language_query}\nOutput:"
        response = model.generate_content(full_prompt)
        return response.text.strip().strip('"')
    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        raise Exception(f"Failed to generate SQL query: {str(e)}")

# Function to generate textual interpretation using Gemini


def generate_textual_interpretation(user_query,sys_prompt, sql_results):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Prepare the prompt for interpretation
        interpretation_prompt = f"""
        {TEXT_INTERPRETATION_PROMPT}

        {sys_prompt}

        Original user question: {user_query}

        Data to interpret: {sql_results}

        Please provide a concise textual interpretation of this data:
        """

        response = model.generate_content(interpretation_prompt)
        print(response)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating textual interpretation: {str(e)}")
        # Fallback: return the raw data if interpretation fails
        return f"Here are the results for your query: {sql_results}"

# Function to execute SQL query


def execute_sql_query(query):
    try:
        connection = mysql.connector.connect(**app.config['MYSQL_CONFIG'])
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Exception as e:
        logger.error(f"Error executing SQL query: {str(e)}")
        raise Exception(f"Database query failed: {str(e)}")

# API endpoint


@app.route('/generate-report', methods=['GET'])
@require_api_key
def generate_report():
    try:
        # Get JSON data from request
        data = request.get_json()

        if not data or 'prompt' not in data:
            return error_response("Missing 'prompt' in request body", 400)

        user_prompt = data['prompt']
        sys_prompt = data['sys_prompt']

        # Generate SQL query using Gemini
        sql_query = generate_sql_query(user_prompt)
        logger.info(f"Generated SQL query: {sql_query}")

        # Execute the query
        results = execute_sql_query(sql_query)
        logger.info(f"Query executed successfully. Returned {
                    len(results)} rows.")

        # Generate textual interpretation using Gemini
        interpretation = generate_textual_interpretation(user_prompt, sys_prompt,results)
        print(interpretation)

        # Prepare response data
        response_data = {
            "text": interpretation,
            "raw_data": results,
            # "query": sql_query
        }

        # Return success response with both interpretation and raw data
        return success_response(data=response_data, message="Report generated successfully")

    except Exception as e:
        logger.error(f"Error in generate-report: {str(e)}")
        return error_response(str(e), 500)

# Health check endpoint


@app.route('/health', methods=['GET'])
def health_check():
    return success_response(message="API is running successfully")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
