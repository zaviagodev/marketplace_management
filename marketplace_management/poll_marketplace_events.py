import frappe
import boto3


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
                print("Received message:", message["Body"])
                
                event_payload = message["Body"]
                # TODO: Process the event_payload

                # Important: Delete the message from the queue after message has been processed
                sqs.delete_message(
                    QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
                )
        else:
            print("No messages available")
