#!/bin/bash
set -e
# set -x

#----- Change these parameters to suit your environment -----#
AWS_PROFILE="default"
AWS_REGION="us-east-1"
BUCKET_NAME="sam-templates-011" # bucket must exist in the SAME region the deployment is taking place
SERVICE_NAME="serverless-thumbnails-creator"
TEMPLATE_NAME="${SERVICE_NAME}.yaml"
STACK_NAME="${SERVICE_NAME}"
OUTPUT_DIR="./outputs/"
PACKAGED_OUTPUT_TEMPLATE="${OUTPUT_DIR}${STACK_NAME}-packaged-template.yaml"

#----- End of user parameters  -----#


# You can also change these parameters but it's not required
# debugMODE="True"

# Package the code
function pack() {

    # Cleanup Output directory
    rm -rf "${OUTPUT_DIR}"*
    echo -e "\n Stack Packaging Initiated \n"
    aws cloudformation package \
        --template-file "${TEMPLATE_NAME}" \
        --s3-bucket "${BUCKET_NAME}" \
        --output-template-file "${PACKAGED_OUTPUT_TEMPLATE}"
    
    exit
}
# Deploy the stack
function deploy() {
    echo -e "\n Stack Deployment Initiated \n"
    aws cloudformation deploy \
        --profile "${AWS_PROFILE}" \
        --template-file "${PACKAGED_OUTPUT_TEMPLATE}" \
        --stack-name "${STACK_NAME}" \
        --tags Service="${SERVICE_NAME}" \
        --capabilities CAPABILITY_IAM \
        --region "${AWS_REGION}"
        # --parameter-overrides \
        #    debugMODE="${debugMODE}" \
    exit
}

function nuke_stack() {
        echo -e "\n Stack Deletion Initiated \n"
		aws cloudformation delete-stack --stack-name "${STACK_NAME}" --region "${AWS_REGION}"
        exit
	}


# Check if we need to destroy the stack
if [ "$1" = "nuke" ]; then
 nuke_stack
  elif [ "$1" = "pack" ]; then
   pack
    elif [ "$1" = "deploy" ]; then
     deploy
fi
