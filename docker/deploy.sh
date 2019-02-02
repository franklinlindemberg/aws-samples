#!/bin/bash

mkdir tmp
mkdir tmp/package

cp -r resources/main tmp/package
cp -r resources/binaries/. tmp/package

python3 -m pip install --upgrade -i https://test.pypi.org/simple/ cognitive-services --extra-index-url https://pypi.org/simple -t tmp/package
python3 -m pip install pydub -t tmp/package

echo Creating lambda.zip
cd tmp/package/
zip -r ../$PACKAGE_ZIP_NAME .
cd -

echo Uploading $PACKAGE_ZIP_NAME to S3://$BUCKET_NAME
aws s3 cp tmp/$PACKAGE_ZIP_NAME  s3://$BUCKET_NAME
echo $PACKAGE_ZIP_NAME uploaded

echo Generating cloud formation template
python3 resources/cf_template.py > tmp/cf_template.json

echo Deploying stack $STACK_NAME
aws cloudformation deploy \
    --stack-name $STACK_NAME \
    --template-file tmp/cf_template.json \
    --capabilities CAPABILITY_IAM
echo Stack deployed successfully