# My-Django-Social-Media
![Alt text](social-media.png?raw=true "Title")
This project aims to implement a similar product like twitter/wechat. 

This project is developed on [`Django`](https://github.com/django/django) under [`Vagrant`](https://github.com/hashicorp/vagrant).

Utilized databases:

1. Relational : [`MySQL`](https://github.com/mysql),
2. NoSQL: [`HBase`](https://github.com/apache/hbase), [`Redis`](https://github.com/redis/redis)

Uploaded the user profile to [`Amazon S3`](https://aws.amazon.com/s3/).

Developed RESTful APIs for accounts, tweets, comments, friendships, likes, notifications, and newsfeeds based on [`Django-Rest-Framework`](https://github.com/encode/django-rest-framework).

Get data from the MessageQueue based on the number of requests that each machine can handle. Even if there are high volume of requests per second, it just puts the requests in the MQ, and the message of the message queue is controlled by the system itself, so that the entire system will not be collapsed.


# Optimizating
1. Optimized tweet and newsfeed pagination by implementing a infinite scroll pagination instead of [`page-number-pagination`](https://github.com/encode/django-rest-framework/blob/master/rest_framework/pagination.py).
2. Utilized [`Redis`](https://github.com/redis/redis): cache lists of tweets and newsfeeds, and utilized Redis as Message Queue Broker to deliver asynchronizedfeeds fanout tasks by using Celery.
3. Utilized [`Memcache`](https://github.com/linsomniac/python-memcached): cache friendship followings and user.
4. Utilized [`Celery`](https://github.com/celery/celery) framework to ensure the stablility of FlashSale system. For example, restrict the request flow on multiple refreshing web page.
5. Utilized [`ratelimiter`](https://github.com/jsocol/django-ratelimit) as a decorator to add limitations on user actions for RESTful APIs.
# Next stage
1. Deploy in a remote server, e.g. AWS
2. Load balance.
