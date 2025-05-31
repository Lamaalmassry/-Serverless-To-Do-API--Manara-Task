resource "aws_lambda_function" "task_handler" {
  function_name = "TaskHandler"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "handler.zip"

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_basic_execution]
}