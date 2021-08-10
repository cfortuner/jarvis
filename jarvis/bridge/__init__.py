import json
import logging

from typing import Callable
from websocket_server import WebsocketServer, WebSocketHandler

class BridgeMessage:
    def __init__(self, messageType: str, data: any):
        self.type = messageType
        self.data = data

class Bridge:
    def __init__(self):
        self.clients = []
        self._server = WebsocketServer(4000, host='127.0.0.1', loglevel=logging.INFO)
        self._server.set_fn_new_client(self._new_client)
        self._server.set_fn_client_left(self._client_left)
        self._server.set_fn_message_received(self._message_received)

        self._subscriptions: dict[str, list[Callable[[BridgeMessage]]]] = {}

    def listen(self):
        self._server.run_forever()

    def _new_client(self, client, _: WebsocketServer) -> None:
        self.clients.append(client)

    def _client_left(self, client, _: WebsocketServer) -> None:
        logging.info(f"client {client['id']} disconnected")

    def _message_received(self, client, _, jsn) -> None:
        jsn = json.loads(jsn)
        print(jsn)

        if 'data' not in jsn:
            jsn['data'] = None

        message = BridgeMessage(jsn['type'], jsn['data'])

        if message.type not in self._subscriptions:
            print(f"Received unknown message from client {message.type} {message.data}")
            return

        for callback in self._subscriptions[message.type]:
            callback(BridgeMessage(message.type, message.data))

    def send_message(self, messageType: str, data: any = None) -> None:
        if data is None:
            self._server.send_message_to_all(json.dumps({ "type": messageType }))
            return

        self._server.send_message_to_all(json.dumps({ "type": messageType, "data": data}))

    def subscribe(self, messageType: str, callback: Callable[[BridgeMessage], None]):
        print(f"Subscribing to message {messageType}")
        if messageType in self._subscriptions:
            print("appending")
            self._subscriptions[messageType].append(callback)
        else:
            self._subscriptions[messageType] = [callback]