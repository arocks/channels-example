# Detailed Steps

## Project 1: Web Socket Echo

### Set up environment: install packages

```
$ cd ~/projs
$ mkdir channels2-example
$ cd channels2-example/
$ pipenv shell
$ pipenv install django
$ pipenv install channels channels-redis
```

### Create new project

```
$ django-admin startproject channelsproj .
$ ./manage.py startapp notifier
```

No need for DB or admin so avoid migrate and create superuser

### Git

Create small `.gitignore`

Init repositories
```
$ git init
$ git add .
$ git commit -m "initial"
```

### Home page

Add the home page you want to show

```
$ mkdir notifier/templates
$ touch notifier/templates/home.html
```

home.html:

```
<html>
  <title>Notifier</title>
  <body>
    <h1>Notifier</h1>
  </body>
</html>
```

notifier/views.py:

```
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home.html"

```


settings.py:

```
...
ALLOWED_HOSTS = ["0.0.0.0"]

...
INSTALLED_APPS = [

...
    'notifier',

```

urls.py:

``` 
from notifier.views import HomeView

...

    path('', HomeView.as_view()),

```

Run server:

```
$ ./manage.py runserver
```

Open http://0.0.0.0:8000/ in browser

### Echoing consumer



settings.py:

```
...
ALLOWED_HOSTS = ["0.0.0.0"]

...
INSTALLED_APPS = [
...
    'channels',
    'notifier',
...

ASGI_APPLICATION = "channelsproj.routing.application"

```

notifier/consumers.py:

```
from channels.consumer import AsyncConsumer


class EchoConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        # Echo the same received payload
        await self.send({
            "type": "websocket.send",
            "text": event["text"]
        })

```

channelsproj/routing.py:

```
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from notifier.consumers import EchoConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/", EchoConsumer),
    ])
})

```

home.html:

```
{% load staticfiles %}
<html>
  <head>
    <title>Notifier</title>
    <script src="{% static '/channels/js/websocketbridge.js' %}" type="text/javascript"></script>
  </head>
  <body>
    <h1>Notifier</h1>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
      const webSocketBridge = new channels.WebSocketBridge();
      webSocketBridge.connect('/ws/');
      webSocketBridge.listen(function(action, stream) {
        console.log("RESPONSE:", action, stream);
      })
      document.ws = webSocketBridge; /* for debugging */
    })
    </script>
  </body>
</html>
```

Open http://0.0.0.0:8000/ in browser
    Point out that the development server is different
    Another port 50642 is used for websockets
Press Ctrl+Shift+I -> Console:
Type: `document.ws.send("Covfefe")`

### Tick Tock Consumer

consumers.py:

```
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TickTockConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        while 1:
            await asyncio.sleep(1)
            await self.send_json("tick")
            await asyncio.sleep(1)
            await self.send_json(".....tock")

```

routing.py:

```
...
from notifier.consumers import TickTockConsumer

...
        path("ws/", TickTockConsumer),

```

home.html:

```
...
        console.log("RESPONSE:", action);

```
Refresh http://0.0.0.0:8000/ in browser
    It should have tick...tocks...

### User Notification Consumer

```
$ ./manage.py migrate
$ ./manage.py createsuperuser

#------- New window
$ sudo pacman -S redis
$ redis-server

#------- Back to same window
$ redis-cli ping
PONG

```
Show REDIS port 6379 then add in settings.py:

```
# Channels settings
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}

```
notifier/__init__.py:

```
default_app_config = 'notifier.apps.NotifierConfig'
```

apps.py:

```
    def ready(self):
        from . import signals

```

signals.py:

``` 
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=User)
def announce_new_user(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "gossip", {"type": "user.gossip",
                       "event": "New User",
                       "username": instance.username})

```

consumers.py:

```
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NoseyConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("gossip", self.channel_name)
        print(f"Added {self.channel_name} channel to gossip")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("gossip", self.channel_name)
        print(f"Removed {self.channel_name} channel to gossip")

    async def user_gossip(self, event):
        await self.send_json(event)
        print(f"Got message {event} at {self.channel_name}")

```

routing.py:

```
from notifier.consumers import NoseyConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("notifications/", NoseyConsumer),
    ])
})

```


home.html:

```
  <body>
    <h1>Notifier</h1>
    <p>Notifications</p>
    <ul id="notifylist"></ul>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
      const webSocketBridge = new channels.WebSocketBridge();
      const nl = document.querySelector("#notifylist");
      
      webSocketBridge.connect('/notifications/');
      webSocketBridge.listen(function(action, stream) {
        console.log("RESPONSE:", action);
        if(action.event == "New User") {
          var el = document.createElement("li");
          el.innerHTML = `New user <b>${action.username}</b> has joined!`;
          nl.appendChild(el);
        }
      })
      document.ws = webSocketBridge; /* for debugging */
    })
    </script>
  </body>

```
Refresh http://0.0.0.0:8000/ in browser
    It should have tick...tocks...

New browser top and bottom split window
Open http://0.0.0.0:8000/admin in that browser
    Create a new user

Notifications will appear!

# Before Screencasts

## Virtual Machine

1. Resize to 1080 by 720 by script
2. Terminal in Desktop 1, Emacs in 2 and Browser in 10

## Emacs 

1. Increase font size (use screencast scripts)
2. Desktop clear (M-x desktop-clear)
3. Turn on speedbar (Win+x) and adjust width
4. Open Emacs outside the virtualbox 
