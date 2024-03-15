import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as archive from "@pulumi/archive";

// package the code
const code = archive
  .getFile({
    type: "zip",
    sourceDir: "./functions",
    excludes: [".env", "node_modules", "venv", ".pulumi"],
    outputPath: "functions_payload.zip",
  })
  .then((result) => result.outputPath);

const node_modules = archive
  .getFile({
    type: "zip",
    sourceDir: "./temp_node_modules",
    outputPath: "nodejs.zip",
  })
  .then((result) => result.outputPath);

// Create an IAM role for the Lambda function
const lambdaRole = new aws.iam.Role("lambdaRole", {
  assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({
    Service: "lambda.amazonaws.com",
  }),
});

// Attach the AWSLambdaBasicExecutionRole policy to the IAM role
new aws.iam.RolePolicyAttachment("lambdaRoleAttachment", {
  role: lambdaRole,
  policyArn: aws.iam.ManagedPolicy.AWSLambdaBasicExecutionRole,
});

// SQS FIFO queue
const marketplaceEventsQueue = new aws.sqs.Queue("marketplaceEventsQueue", {
  fifoQueue: true,
  contentBasedDeduplication: true,
  messageRetentionSeconds: 1209600, // 14 days
});

const sendMessagesPolicy = new aws.iam.Policy("sendMessagesPolicy", {
  description: "Allow Lambda function to send messages to SQS queue",
  policy: {
    Version: "2012-10-17",
    Statement: [
      {
        Effect: "Allow",
        Action: "sqs:SendMessage",
        Resource: marketplaceEventsQueue.arn,
      },
    ],
  },
});

new aws.iam.PolicyAttachment("sendMessagesPolicyAttachment", {
  roles: [lambdaRole],
  policyArn: sendMessagesPolicy.arn,
});

// LAYERS
const nodeModulesLayer = new aws.lambda.LayerVersion("nodeModulesLayer", {
  layerName: "nodeModulesLayer",
  compatibleRuntimes: ["nodejs18.x"],
  code: new pulumi.asset.FileArchive(node_modules),
});

// Create a Lambda function
const marketplaceEventsReceverFunction = new aws.lambda.Function(
  "marketplaceEventsReceverFunction",
  {
    runtime: aws.lambda.Runtime.NodeJS18dX,
    role: lambdaRole.arn,
    handler: "marketplaceEventsRecever.handler",
    code: new pulumi.asset.FileArchive(code),
    layers: [nodeModulesLayer.arn],
    timeout: 60,
    environment: {
      variables: {
        QUEUE_URL: marketplaceEventsQueue.url,
      },
    },
  }
);

// Function URL to enable HTTPS access to the Lambda function
const marketplaceEventsReceverFunctionURL = new aws.lambda.FunctionUrl(
  "marketplaceEventsReceverFunctionURL",
  {
    functionName: marketplaceEventsReceverFunction.name,
    authorizationType: "NONE", // No authorization required for this example
    cors: {
      allowOrigins: ["*"],
      allowMethods: ["*"],
    },
  }
);

// Export the HTTPS endpoint URL
export const url = marketplaceEventsReceverFunctionURL.functionUrl;
