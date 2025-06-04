import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))  # useful for debugging in CloudWatch

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Max-Age": "86400"
    }

    # Detect HTTP method robustly (support REST API and HTTP API)
    method = event.get("requestContext", {}).get("http", {}).get("method") \
        or event.get("httpMethod", "GET")

    path = event.get("requestContext", {}).get("http", {}).get("path") \
        or event.get("path", "/")

    # Handle OPTIONS preflight
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight successful'})
        }

    try:
        path_parts = [p for p in path.split('/') if p]
        task_id = path_parts[-1] if len(path_parts) > 1 else None

        # Handle POST
        if method == 'POST':
            data = json.loads(event['body'])
            if not data.get('title'):
                raise ValueError("Title is required")

            task = {
                'taskId': str(uuid.uuid4()),
                'title': data['title'],
                'status': data.get('status', 'Pending'),
                'description': data.get('description', ''),
                'priority': data.get('priority', 'medium'),
                'due_date': data.get('due_date', ''),
                'createdAt': datetime.now().isoformat()
            }

            table.put_item(Item=task)
            return {
                'statusCode': 201,
                'headers': headers,
                'body': json.dumps(task)
            }

        # Handle GET
        elif method == 'GET':
            if task_id:
                response = table.get_item(Key={'taskId': task_id})
                if 'Item' not in response:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({'error': 'Task not found'})
                    }
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(response['Item'])
                }
            else:
                response = table.scan()
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(response.get('Items', []))
                }

        # Handle PUT
        elif method == 'PUT' and task_id:
            data = json.loads(event['body'])
            update_expression = []
            expression_vals = {}

            for field in ['title', 'description', 'status', 'priority', 'due_date']:
                if field in data:
                    update_expression.append(f"{field} = :{field}")
                    expression_vals[f":{field}"] = data[field]

            if not update_expression:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'No valid fields to update'})
                }

            table.update_item(
                Key={'taskId': task_id},
                UpdateExpression='SET ' + ', '.join(update_expression),
                ExpressionAttributeValues=expression_vals,
                ReturnValues='ALL_NEW'
            )

            updated = table.get_item(Key={'taskId': task_id})['Item']
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(updated)
            }

        # Handle DELETE
        elif method == 'DELETE' and task_id:
            table.delete_item(Key={'taskId': task_id})
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'Task deleted successfully'})
            }

        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
