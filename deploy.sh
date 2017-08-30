#!/bin/bash

zip -r twit.zip api/ 
zip -u twit.zip main.py

BUCKET=ca-serverless-demo-py
REGION=us-east-2

aws s3 mb s3://$BUCKET --region $REGION || true
aws s3 cp twit.zip s3://$BUCKET --region $REGION
aws s3api put-bucket-policy --bucket $BUCKET --policy file://s3_policy.json

aws cloudformation deploy --template-file ./template.yml --stack-name anony-twit  --capabilities CAPABILITY_IAM --region $REGION
# On failure
# aws cloudformation describe-stack-events --stack-name anony-twit

# Set permissions so that API Gateway can invoke the function. 
# Shouldn't have to do this here. Not sure how to make it work with CF though...YET!
# https://www.youtube.com/watch?v=H4LM_jw5zzs
API_GATEWAY=$(aws apigateway get-rest-apis | python -c "import json, sys; s = json.loads(sys.stdin.read()); print([i['id'] for i in s['items'] if i['name'] == 'anony-twit'].pop())")

# For each func in $(aws lambda list-functions) where Functions[n].FunctionName like 'anony-twit'

IFS=',' read -r -a array <<< $(aws lambda list-functions | python -c "import json, sys; s = json.loads(sys.stdin.read()); print(','.join([i['FunctionName'] for i in s['Functions'] if i['FunctionName'].startswith('anony-twit')]))")

for i in "${array[@]}"
do
   aws lambda add-permission --function-name "$i" --statement-id lambda-anony-twit-$(((RANDOM % 10000) + 1)) --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn "arn:aws:execute-api:us-east-2:425607006828:$API_GATEWAY/*/*/*"
done

