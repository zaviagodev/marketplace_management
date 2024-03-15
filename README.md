# Marketplace Management

## Project Overview

Marketplace Management is a project designed to integrate with a marketplace API and manage events through an AWS SQS queue. The project is split into two parts: a TypeScript project managed with Pulumi for infrastructure setup and a Python project for application logic.

## Infrastructure

The infrastructure for this project is managed using Pulumi, a modern infrastructure as code tool. The infrastructure includes an AWS SQS FIFO queue for managing marketplace events and an AWS Lambda function that receives events from the marketplace API and sends them to the SQS queue.

Here's a simple diagram to visualize the infrastructure:

| | | | | | | Marketplace API +-----> AWS Lambda Func +-----> AWS SQS Queue <-----+ bench marketplace-poll worker | | | | | | |

## Getting Started

To start polling the marketplace, you need to complete the following steps:

### 1. configure custom queue

add the following to your `site_config.json` file:

```json
"workers": {
        "marketplaceEventsQueue": {
            "timeout": "3650d",
            "background_workers": 1
        }
    }
```

### 2. configure the marketplace-polling worker

You need to run the following command to `Procfile`:

```bash
marketplaceEventsWorker: bench worker --queue marketplaceEventsQueue>> logs/marketplaceEventsWorker.log 2>> logs/marketplaceEventsWorker.error.log
```

### 3. start marketplace-polling worker

```bash
bench marketplace-polling on \
--site <site-name> \
--queue-url https://sqs.<aws-region>.amazonaws.com/<your-aws-account-id>/marketplaceEventsQueue.fifo \
--aws-access-key-id <your-aws-access-key-id> \
--aws-secret-access-key <your-aws-secret-access-key> \
--region ap-southeast-1 \
--queue marketplaceEventsQueue
```

This command will start polling from SQS and send the events downstream sites.

To stop polling the marketplace, you need to run the following command:

```bash
bench marketplace-polling off \
--site <site-name>
```
