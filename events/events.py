import requests
import pandas as pd
import json
from datetime import datetime, date
import os
import boto3

DATA_URL = os.environ['RESTAURANTS_URL']
BUCKET_NAME = os.environ['BUCKET_NAME']

def dateOverlap(start_date: date, end_date: date, event_month: date):
    # returns True if any date within the start and end dates falls in the event_month
    if start_date.year == event_month.year and start_date.month == event_month.month: 
        return True
    elif end_date.year == event_month.year and end_date.month == event_month.month:
        return True
    elif start_date < event_month and end_date > event_month:
        return True
    else:
        return False

def get_data(url = DATA_URL):
    r = requests.get(url)
    json_data = json.loads(r.text)
    return json_data

def handleMissing(d, key):
    try:
        return d[key]
    except (IndexError, KeyError) as e:
        return 'NA'


def get_events(json_data, event_month=date(2017,4,1)):
    res_list = []
    c=0
    for i in json_data:
        try: # skip if restaurants is not a key
            for j in i['restaurants']:
                restaurant = j['restaurant']
                try: # skip if no events
                    for event in restaurant['zomato_events']:
                        start_date = datetime.strptime(event['event']['start_date'], '%Y-%m-%d').date()
                        end_date = datetime.strptime(event['event']['end_date'], '%Y-%m-%d').date()
                        if dateOverlap(start_date, end_date, event_month):
                            res_list.append({
                                'event_id': handleMissing(event['event'], 'event_id'),
                                'restaurant_id': handleMissing(restaurant['R'], 'res_id'),
                                'restaurant_name': handleMissing(restaurant, 'name'),
                                #'photo_url': handleMissing(event['event']['photos'][0]['photo'], 'url'),
                                'event_title': handleMissing(event['event'], 'title'),
                                'event_start_date': start_date,
                                'event_end_date': end_date
                            })
                            try:
                                res_list[-1]['photo_url'] = handleMissing(event['event']['photos'][0]['photo'], 'url')
                            except IndexError:
                                res_list[-1]['photo_url'] = 'NA'
                except KeyError:
                    continue
        except KeyError:
            continue

    return pd.DataFrame(res_list)

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
    df = get_events(j)
    df.to_csv('/tmp/events.csv', index=False)
    csv_link = upload_file('/tmp/events.csv', BUCKET_NAME, object_name='output/events.csv')
    
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
