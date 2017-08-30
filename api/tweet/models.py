import boto3
import os
import uuid
import datetime
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal 


class Tweet(object):
    ''' Tweet provides functions to get and save tweets. 
        Usage:  
            tweet = Tweet("This is my tweet!", "LISTEN TO ME!!!!!")
            tweet.save()
            
            To get all tweets for a given day
            tweets = Tweet()
            tweets.all() <-- all tweets for today (server time)
            tweets.all(starting_date=datetime.date(2017,08,10)) <-- all tweets for August 10th, 2017
            tweets.all(today_minus=1) <-- all tweets for yesterday (server time)
    '''
    id = None
    content = None
    header = None
    created = None

    whitelist = ['content', 'header'] # Determines which properties a user can set.
    
    def __init__(self, content=None, header=None, client=None, region=None, table=None):
        if client is None:
            self.client = boto3.resource('dynamodb', region_name=region or 'us-east-2')
        # Try and pull from ENV VARS. If that fails use the hardcoded string
        self.table = table or self.client.Table(os.getenv('TWEET_TABLE', 'tweets'))
        self.content = content
        self.header = header

    def init_from_dict(self, properties, whitelist=None):
        ''' init_from_dict takes a dict and sets any properties that are in the whitelist.
            Use case for this is setting properties from an untrusted source such as a POST body.
        '''
        if (not isinstance(properties, (dict,))):
            raise ValueError('The properties argument should be a dict.')
        
        if whitelist is None:
            whitelist = self.whitelist
        for k, v in properties.items():
            if k in whitelist and hasattr(self, k):
                setattr(self, k, v)
        
        return self
    
    def to_dict(self):
        return { 
            'id': self.id, 
            'content': self.content, 
            'header': self.header, 
            'created': str(self.created_datetime())
        }
        
    
    def save(self):
        ''' Save the current record. '''
        if self.content is None or len(self.content) == 0:
            raise ValueError('content cannot be null or empty')
        
        if self.id is None:
            self.id = str(uuid.uuid4())
        
        if self.created is None:
            self.created =  Decimal(datetime.datetime.now().timestamp())
        
        # Probably won't need the results, but I'll return 'em for this demo
        return self.table.put_item(Item={
            'id': self.id,
            'content': self.content,
            'created': self.created,
            'created_key': self.created_key(),
            'header': self.header or ''
        })
    
    def all(self, today_minus=0, starting_date=None ):
        response = self.table.query(
            KeyConditionExpression=Key('created_key').eq(self.created_key(today_minus, starting_date)) 
        )
        if 'Items' in response:
            return [Tweet().init_from_dict(item, self.whitelist + ['created', 'created_key', 'id']) for item in response['Items']]
    
    def created_datetime(self):
        return datetime.datetime.fromtimestamp(self.created)

    def created_key(self, today_minus=0, starting_date=None):
        ''' created_key returns a date string representing the 
            YYYY MM DD that a record was created on. This allows for lookups by day.
            This is not an exceptionally scalable method. However, it works for this demo.
        '''
        d = (starting_date or datetime.date.today()) - datetime.timedelta(days=today_minus)
        return int(d.strftime('%Y%m%d'))
