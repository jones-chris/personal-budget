#!/bin/bash

PROJECT_VERSION=$1
ZIP_FILE="personal-budget-$PROJECT_VERSION.zip"

# Upload zip file to S3.  This is done manually rather than having CodeBuild do this at the end of the build because
# CloudFormation will need the zip file loaded into S3 before it can deploy it in the next step.  If CodeBuild uploaded
# the file to S3 at the end of the build, then the zip file wouldn't exist in S3 for the CloudFormation deployment.
aws s3 cp "$ZIP_FILE" s3://my-personal-budget/"$ZIP_FILE"

# Deploy CloudFormation Templates.
aws cloudformation deploy --template-file ./cicd/cloudformation/stacks/dynamo-personal-budget-transactions.cloudformation.yml \
                            --stack-name personal-budget-dynamo-tables \
                            --capabilities CAPABILITY_NAMED_IAM

aws cloudformation deploy --template-file ./cicd/cloudformation/stacks/daily-etl-lambda.cloudformation.yml \
                            --stack-name personal-budget-daily-etl \
                            --capabilities CAPABILITY_NAMED_IAM \
                            --parameter-overrides Version="$PROJECT_VERSION"

