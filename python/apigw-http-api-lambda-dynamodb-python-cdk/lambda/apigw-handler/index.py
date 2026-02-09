# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def log_event(level, message, **kwargs):
    """Helper function for structured logging"""
    log_entry = {
        "message": message,
        **kwargs
    }
    logger.log(level, json.dumps(log_entry))


def handler(event, context):
    table = os.environ.get("TABLE_NAME")
    request_context = event.get("requestContext", {})
    
    log_event(
        logging.INFO,
        "Processing request",
        request_id=request_context.get("requestId"),
        source_ip=request_context.get("identity", {}).get("sourceIp"),
        http_method=request_context.get("httpMethod"),
        table_name=table
    )
    
    try:
        if event["body"]:
            item = json.loads(event["body"])
            year = str(item["year"])
            title = str(item["title"])
            id = str(item["id"])
            dynamodb_client.put_item(
                TableName=table,
                Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
            )
            log_event(
                logging.INFO,
                "Successfully inserted data",
                request_id=request_context.get("requestId"),
                operation="put_item",
                status="success",
                item_id=id
            )
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
        else:
            item_id = str(uuid.uuid4())
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "year": {"N": "2012"},
                    "title": {"S": "The Amazing Spider-Man 2"},
                    "id": {"S": item_id},
                },
            )
            log_event(
                logging.INFO,
                "Successfully inserted default data",
                request_id=request_context.get("requestId"),
                operation="put_item",
                status="success",
                item_id=item_id
            )
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
    except Exception as e:
        log_event(
            logging.ERROR,
            "Error processing request",
            request_id=request_context.get("requestId"),
            error=str(e),
            status="failure"
        )
        raise
