## POST FUNCTIONS FOR PASTE BUCKET ##
##  AUTHOR: Thomas Ward (s3659610)  ##
from decimal import Decimal
import base64
import boto3
import time
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from flask import jsonify, request

def pasteText(type, post_id, post, title, description, views, author, delete_time, burn, time_posted, ip_address, user):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('posts')
    try:
        post = table.put_item(
            Item={
                'type': type,
                'post_id': post_id,
                'post':post,
                'title':title,
                'description':description,
                'page_views':views,
                'author':author,
                'delete-time':delete_time,
                'burn': burn,
                'time-posted': time_posted,
                'ip-address': ip_address,
                'user':user
            }
        )
        return True
    except Exception as e:
        print(e)
        return False


def addView(post_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('posts')
    new_view = Decimal(int(getPasteTypeText(post_id)['page_views'])+1)
    try:
        response = table.update_item(
            Key={
                'post_id': post_id
            },
            UpdateExpression="SET page_views=:v",
            ExpressionAttributeValues={
                ':v': new_view,
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    except Exception as e:
        print(e)
        return False

def getPasteTypeText(post_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('posts')
    try:
        response = table.get_item(Key={'post_id': post_id})
        try:
            if (response['Item']):

                if(response['Item']['delete-time'] == ""):
                    hoursLeft = "burn on reading"
                else:
                    hoursLeft = str(round(((int(response['Item']['delete-time']) - int(time.time()))/ 60 / 60),2)) + "Hours"

                response['Item']['hoursLeft'] = hoursLeft
                return response['Item']
        except Exception as e:
            print("post doesnt exist")
            return False

    except ClientError as e:
        print(e.response['Error']['Message'])
        return False

    return False


def getUserPosts(username):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('posts')
    try:
        posts = []
        response = table.scan(
            FilterExpression=Attr('user').eq(username)
        )
        for post in response["Items"]:
            if (post['delete-time'] == ""):
                hoursLeft = "Will Destory On Reading"
                post['description'] = "DESCRIPTION IS HIDDEN"
            else:
                hoursLeft = str(round(((int(post['delete-time']) - int(time.time()))/ 60 / 60),2) ) + " Hours"

            post['hoursLeft'] = hoursLeft
            posts.append(post)

        return posts
    except ClientError as e:
        print(e.response['Error']['Message'])

    return False

def getTrendingPosts():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('posts')
    trending = []
    try:
        response = table.scan(
            FilterExpression=Key('page_views').gt(5),
        )

        for post in response["Items"]:
            if (post['delete-time'] == ""):
                hoursLeft = "Will Destory On Reading"
                post['description'] = "DESCRIPTION IS HIDDEN"
            else:
                hoursLeft = str((int(post['delete-time']) - int(time.time()) / 60 / 60)) + " Hours"

            post['hoursLeft'] = hoursLeft
            post['description'] = post['description'][:30] + "..."
            post['title'] = post['title'][:13]
            post['author'] = post['author'][:10]

            trending.append(post)

        trending = response["Items"][:5]
        return trending
    except Exception as e:
        print("err in trending")
        print(e)
        return None


def getRecentPosts():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('posts')
    try:
        response = table.scan(
            IndexName="post_id-time-posted-index"
        )


        newResponse = sorted(response['Items'], key=lambda i: i['time-posted'], reverse=True)[:5]
        return orderRecentPosts(newResponse)
    except Exception as e:
        print("err in recent")
        print(e)
        return None


def orderRecentPosts(response):
    recentPosts = []
    # add attiubte been alive to a post to items
    for item in response:
        currentTime = int(time.time())
        item['beenAlive'] = round( (currentTime - int(item['time-posted'])) /60/60, 2)
        item['title'] = item['title'][:10] + "..."
        if(item['burn'] == 1):
            item['description'] = "DESCRIPTION IS HIDDEN"
        item['description'] = item['description'][:25] + "..."
        item['title'] = item['title'][:20]
        item['author'] = item['author'][:9]

    return response

def getGlobal():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('posts')
    try:
        response = table.scan(
            IndexName="post_id-time-posted-index"
        )




        for post in response["Items"]:
            if (post['delete-time'] == ""):
                hoursLeft = "Will Destory On Reading"
                post['description'] = "DESCRIPTION IS HIDDEN"
            else:
                hoursLeft = round(((int(post['delete-time']) - int(time.time()))/ 60 / 60),2)

            post['hoursLeft'] = hoursLeft
            post['description'] = post['description'][:30] + "..."
            post['title'] = post['title'][:25] + "..."

        newResponse = sorted(response['Items'], key=lambda i: i['time-posted'])
        return newResponse
    except Exception as e:
        print(e)
        return None

def burnPost(post_id):
    # given post id delete post from db
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('posts')
    try:
        response = table.delete_item(
            Key={
                'post_id': post_id
            }
        )
        print(response)
        return response
    except ClientError as e:
        print(e)
        print("error deleting")
        return False


def pasteImage(type, post_id, post, title, description, views, author, delete_time, burn, time_posted, ip_address, user, image, fileType):
    # add image paste to db
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('posts')
    try:
        post = table.put_item(
            Item={
                'type': type,
                'post_id': post_id,
                'title': title,
                'page_views': views,
                'description':description,
                'post': post,
                'author': author,
                'delete-time': delete_time,
                'burn': burn,
                'time-posted': time_posted,
                'ip-address': ip_address,
                'user': user,
                'fileType':fileType
            }
        )
        # upload image here i.e. call uploadImage with image and post id

        try:
            # upload image
            uploadImage(image, post_id)
        except Exception as e:
            print("error in uploading image")
            print(e)


        return True
    except Exception as e:
        print(e)
        return False



def uploadImage(image, post_id):
    s3 = boto3.client('s3')
    bucket = "paste-bucket-images"
    # Upload the file
    s3_client = boto3.client('s3')

    fileType = image.filename[image.filename.index(".") + 0:image.filename.rindex(".") + 4]
    file = "{}".format(image)
    # object name post-id
    object_name = post_id + fileType
    print(object_name)

    # boiler plate image that gets rename to correct image type when uploaded to s3
    image.save("uploadfile.file")

    try:
        response = s3_client.upload_file("uploadfile.file", bucket, object_name)

        # remove uploadfile.file
        return True
    except Exception as e:

        print(e)
        return False

def getImage(post_id, fileType):
    s3 = boto3.resource('s3')
    try:
        obj = s3.Object("paste-bucket-images", post_id+fileType)
        body = obj.get()['Body'].read()
        encoded_data = base64.b64encode(body).decode("utf-8")
        image = encoded_data
        return image
    except Exception as e:
        print(e)
        print("error in finding post on server")
        return None
