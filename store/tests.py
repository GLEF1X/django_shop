# Create your tests here.
from django.test import Client

c = Client()
response = c.get(path='/p/5mWr1ar7/',
                 content_type='text/plain')
