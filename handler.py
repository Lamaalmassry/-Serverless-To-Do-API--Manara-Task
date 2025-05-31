import json
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    method = event['requestContext']['http']['method']
    path = event['requestContext']['http']['path']
    path_parts = path.strip("/").split("/")
    task_id = path_parts[-1] if len(path_parts) > 1 else None

    if method == "POST":
        data = json.loads(event['body'])
        task = {
            "taskId": str(uuid.uuid4()),
            "title": data.get('title', ''),
            "status": "Pending",
            "description": data.get("description", ""),
            "priority": data.get("priority", ""),
            "due_date": data.get("due_date", "")
        }
        table.put_item(Item=task)
        return {"statusCode": 201, "body": json.dumps(task)}

    elif method == "GET":
        response = table.scan()
        return {"statusCode": 200, "body": json.dumps(response['Items'])}

    elif method == "PUT" and task_id:
        data = json.loads(event['body'])

        # Prepare update expression for all fields sent
        update_expr = "set " + ", ".join(f"{k}=:{k}" for k in data.keys())
        expr_vals = {f":{k}": v for k, v in data.items()}

        table.update_item(
            Key={"taskId": task_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_vals
        )

        # Return the updated item after update (optional)
        updated_item = table.get_item(Key={"taskId": task_id}).get('Item', {})
        return {"statusCode": 200, "body": json.dumps(updated_item)}

    elif method == "DELETE" and task_id:
        table.delete_item(Key={"taskId": task_id})
        return {"statusCode": 200, "body": json.dumps({"message": "Task deleted"})}

    return {"statusCode": 400, "body": "Unsupported method"}
