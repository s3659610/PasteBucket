## LOGIN FUNCTIONS FOR PASTE BUCKET ##
##  AUTHOR: Thomas Ward (s3659610)  ##
import boto3
import time
from botocore.exceptions import ClientError
from flask import jsonify, request



def sign_up(username, password):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('users')
    try:
        user = table.put_item(
            Item={
                'username': username,
                'password': password,
                'ip-address': request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
                'time-registered': int(round(time.time() * 1000))
            }
        )
        print(user)
        return user
    except Exception as e:
        print(e)

    return None

def check_username_exists(username):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('users')
    try:
        response = table.get_item(Key={'username': username})
        try:
            if (response['Item']):
                return True
        except Exception as e:
            print("username doesnt exits")
            return False

    except ClientError as e:
        print(e.response['Error']['Message'])

    return False


def sign_in(username, password):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('users')
    try:
        response = table.get_item(
            Key={'username': username},
            AttributesToGet=['password', 'username']
        )
        try:
            if (response['Item']):
                # user exists check if password is equql to passowrd
                if (response['Item']['password'] == password):
                    print("password correct")
                    user = response['Item']['username']
                    return user
                else:
                    print("password incorrect")
                    return None
        except Exception as e:
            print("user doesnt exits")
            return None


    except ClientError as e:
        # user doesnt exists
        print(e.response['Error']['Message'])

    return None


def getImage(post_id):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket("paste-bucket-images")
    object = bucket.Object('test.jpg')
    body = object.get()['Body'].read()

    return body
