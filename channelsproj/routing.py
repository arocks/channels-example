from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from notifier.consumers import EchoConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/", EchoConsumer),
    ])
})
