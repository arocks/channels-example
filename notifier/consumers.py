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
