# Food-Travel
This project will deploy 2 AWS lambda functions to perform the necessary analysis. The results of the analysis will be uploaded into an S3 bucket.

## Requirements
[Serverless](https://www.serverless.com/framework/docs/getting-started/)

AWS account (Access Key and Secret Access Key for IAM role with Read/Write Permissions for S3, Lambda)
[Instructions](https://www.serverless.com/framework/docs/providers/aws/cli-reference/config-credentials/) for configuring credentials

Python 3, Pip

## Installation
```
git clone https://github.com/Akmal-Faiz/food-travel.git
pip install -r requirements.txt --target=/layers/python
```

