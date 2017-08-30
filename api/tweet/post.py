import json
import logging
from api.tweet.models import Tweet
# For this demo, let's log ALL THE THINGS!
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    # In a real app error messages shouldn't be sent to the end user.
    # This is a security concern. However, in a demo, for debugging, it's okay.
    body = {}
    if err:
        body = json.dumps({'error': err})
    else:
        body = json.dumps(res)
    return {
        'statusCode': '400' if err else '200',
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def handler(event, context):
    tweet = None
    exception = None
    try:
        tweet = Tweet()
        tweet.init_from_dict(json.loads(event['body']))
        tweet.save()
        logging.info("Tweet with id {} saved!".format(tweet.id))
    except Exception as ex:
        exception = ex.args[0]
        tweet = None
        logging.error("Error saving tweet in get.py. Message: {}".format(exception))

    return respond(exception, tweet.to_dict() if tweet else {})


        
