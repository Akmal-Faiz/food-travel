import requests
import pandas as pd
import json
from datetime import datetime, date
import os
import boto3

DATA_URL = os.environ['RESTAURANTS_URL']
BUCKET_NAME = os.environ['BUCKET_NAME']
COUNTRY_LOOKUP = {
    1: 'India',
    14: 'Australia',
    30: 'Brazil',
    37: 'Canada',
    94: 'Indonesia',
    148: 'New Zealand',
    162: 'Phillipines',
    166: 'Qatar',
    184: 'Singapore',
    189: 'South Africa',
    191: 'Sri Lanka',
    208: 'Turkey',
    214: 'UAE',
    215: 'United Kingdom',
    216: 'United States',
}


def get_data(url = DATA_URL):
    r = requests.get(url)
    json_data = json.loads(r.text)
    return json_data

def json_to_df(json_data):
    res_list = []
    c = 0
    for i in json_data:
        try: # skip if restaurants is not a key
            for j in i['restaurants']:
                restaurant = j['restaurant']
                res_list.append({
                    'restaurant_id': restaurant['R']['res_id'],
                    'restaurant_name': restaurant['name'],
                    'country_name':  COUNTRY_LOOKUP[restaurant['location']['country_id']],
                    'city_name': restaurant['location']['city'],
                    'user_rating_votes': restaurant['user_rating']['votes'],
                    #'user_aggregate_ratings': float(restaurant['user_rating']['aggregate_rating']),
                    'user_rating_text' : restaurant['user_rating']['rating_text'],
                    'cuisines': restaurant['cuisines']
                })
        except KeyError:
            continue
    df = pd.DataFrame(res_list)
    return df


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL': 'public-read'})
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return 'https://%s.s3-%s.amazonaws.com/%s' % (BUCKET_NAME, os.environ['AWS_REGION'], object_name)


def handler(event, context):
    j = get_data()
    df = json_to_df(j)
    df.to_csv('/tmp/data.csv', index=False)
    csv_link = upload_file('/tmp/data.csv', BUCKET_NAME, object_name='output/data.csv')
    
    
    body = {
        "message": "success",
        "csv_link": csv_link,
        "input": event
    }

    response = {    
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


