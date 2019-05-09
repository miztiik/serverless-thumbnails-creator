#!/bin/bash
set -e

#----- Change these parameters to suit your environment -----#
AWS_PROFILE="default"
BUCKET_NAME="sam-templates-011" # bucket must exist in the SAME region the deployment is taking place
SERVICE_NAME="serverless-thumbnails-creator"
TEMPLATE_NAME="${SERVICE_NAME}.yaml"
STACK_NAME="${SERVICE_NAME}"
OUTPUT_DIR="./outputs/"
PACKAGED_OUTPUT_TEMPLATE="${OUTPUT_DIR}${STACK_NAME}-packaged-template.yaml"

#----- End of user parameters  -----#


# You can also change these parameters but it's not required
# debugMODE="True"

    # Cleanup Output directory
rm -rf "${OUTPUT_DIR}"*

echo -n "Stack Packing Initiated"
aws cloudformation package \
    --template-file "${TEMPLATE_NAME}" \
    --s3-bucket "${BUCKET_NAME}" \
    --output-template-file "${PACKAGED_OUTPUT_TEMPLATE}"
    

# Deploy the stack
echo -n "Stack Deployment Initiated"
aws cloudformation deploy \
    --profile "${AWS_PROFILE}" \
    --template-file "${PACKAGED_OUTPUT_TEMPLATE}" \
    --stack-name "${STACK_NAME}" \
    --tags Service="${SERVICE_NAME}" \
    --capabilities CAPABILITY_IAM
    # --parameter-overrides \
    #    debugMODE="${debugMODE}" \
