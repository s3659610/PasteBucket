## LAMBDA FUNCTION FOR IMAGE DELETION
import json

import boto3

def lambda_handler(event, context):
    # TODO implement
    # given a tigger in our case we want to trigger this function on the event of a dynamoDB deletion in our posts table.
    # get post id check weather or not such a post is an image post 
    # if: such post is an image find if s3 has a object with the posts_id i.e. it's corrsponding image
    # if it does then delete image
    # if not do nothing, and end function with no action.
    
    for record in event["Records"]:
        if(record["eventName"] == "REMOVE"):
            # item been delelted we need to check if its an image first
            if(record['dynamodb']['OldImage']['type']['S'] == "image"):
                post_id = record['dynamodb']['Keys']['post_id']['S']
                file_name = post_id + str(record['dynamodb']['OldImage']['fileType']['S'])
                print("Image being deleted!")
                if(deleteImageFromS3(post_id, file_name)):
                    print("image {} deleted successfully".format(file_name))
                else:
                    print("errror in deleting image {} from s3".format(file_name))
                return None
            else:
                return None
        else:
            return None


def deleteImageFromS3(post_id, file_name):
    s3 = boto3.resource('s3')
    bucket = "paste-bucket-images"
    try:
        obj = s3.Object(bucket, file_name)
        obj.delete()
        return True
    except Exception as e:
        print(e)
        return False
