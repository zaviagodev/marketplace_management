exports.handler = async function (event) {
    const AWS = require('aws-sdk');
    const sqs = new AWS.SQS();
    const queueUrl = process.env.QUEUE_URL;

    // Process the event and create a message to send to the FIFO queue
    // This is a placeholder logic
    console.log('Received event:', JSON.stringify(event, null, 2));
    const messageBody = JSON.stringify(event);
    // TODO: add verification logic here

    // if verified successfully, Push the message to the SQS FIFO queue
    await sqs.sendMessage({
        QueueUrl: queueUrl,
        MessageBody: messageBody,
        MessageGroupId: 'default', // MessageGroupId is required for FIFO queues
    }).promise();

    return { statusCode: 200, body: 'Event processed.' };
};