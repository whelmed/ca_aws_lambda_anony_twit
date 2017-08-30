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
    # The only expected failures will be from connection issues to the DB.
    tweets = []
    exception = None
    try:
        tweets = Tweet().all()
        logging.info("{} tweets fetched".format(len(tweets)))
    except Exception as ex:
        exception = ex.args[0]
        logging.error("Could not fetch tweets in get.py. Message: {}".format(exception))

    return respond(exception, [t.to_dict() for t in tweets] )


        
