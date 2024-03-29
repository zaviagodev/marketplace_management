import frappe
import boto3
import json
from marketplace_management.auth.webhook_mange import handle_shopee_webhooks,handle_lazada_webhook

def poll_marketplace_events(
    queue_url, aws_access_key_id, aws_secret_access_key, region_name
):
    # Set up SQS client
    sqs = boto3.client(
        "sqs",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )

    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,  # Maximum number of messages to receive
            WaitTimeSeconds=20,  # Wait time in seconds for long polling
        )

        if "Messages" in response:
            for message in response["Messages"]:
                #print("Received:", message["Body"])

                try:
                    event_payload = json.loads(message["Body"])
                    marketplace_event =  json.loads(event_payload["body"])
                    
                    if marketplace_event.get('source') == "SHOPEE":
                        handle_shopee_webhooks(event_payload["body"])
                    else:
                        handle_lazada_webhook(event_payload["body"])
                    
                    # Important: Delete the message from the queue after message has been processed
                    sqs.delete_message(
                        QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
                    )
                except Exception as e:
                    print(f"Error processing message: {e}")
                    frappe.log_error(frappe.get_traceback(), "poll_marketplace_events")

        else:
            print("No messages availablez") 