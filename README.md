# Django Channels Examples

Examples of asynchronous projects with Django Channels 2. Check out:

* Detailed article: https://arunrocks.com/understanding-django-channels/
* Explainer video: https://www.youtube.com/watch?v=G_EM5WM_08Q

## Setup

Use the pipenv tool

``` shellsession
$ pip install pipenv
$ cd <proj-dir>
$ pipenv install
```

Start the redis server (and make sure it is running in the background)

``` shellsession
$ redis-server
```

Now you need to enter the pipenv shell to run the examples:

``` shellsession
$ pipenv shell
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
```

You should see no notifications. Now open another browser window and log into Django admin. Add a new user. If you look
at the first browser windows, then you should see the new user notification.

### Other Examples

Check out other branches of this git repository to see the other examples:

* [EchoConsumer](https://github.com/arocks/channels-example/tree/EchoConsumer)
* [TickTock](https://github.com/arocks/channels-example/tree/TickTock)
