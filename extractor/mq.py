from distutils.log import error
from threading import Thread
import pika
from pika.adapters.blocking_connection import BlockingChannel
from typing import Any, Callable, Dict, List, Optional, cast
import json

class _Listener:
    def __init__(self, chan: BlockingChannel) -> None:
        self.chan = chan
        self.thread = cast(Optional[Thread], None)

    def __del__(self):
        self.stop()

    def start(self):
        self.thread = Thread(target=self.chan.start_consuming)
        self.thread.start()

    def stop(self):
        if self.thread:
            self.chan.stop_consuming()
            self.thread = None

class QueueManager:
    def __init__(self, param: Optional[pika.ConnectionParameters]=None) -> None:
        self.param = param or pika.ConnectionParameters(
            host='localhost',
            port=5672,
        )
        self.conn = pika.BlockingConnection(self.param)
        self.listen_map = cast(Dict[str, _Listener], {})

    def __del__(self):
        self.conn.close()
    
    def send_object_by_json(self, queue_name: str, obj):
        conn = self.conn

        with conn.channel() as chan:
            chan.queue_declare(queue=queue_name)
            chan = chan.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(obj).encode(),
            )


    def listen_on(self, queue_name: str, callback: Callable[[str], None]):
        def callback_wrap(ch, method, properties, body: bytes):
            body_str = body.decode()
            callback(body_str)
        
        conn = self.conn

        chan = conn.channel()
        chan.queue_declare(queue=queue_name)
        chan.basic_consume(
            queue=queue_name, 
            on_message_callback=callback_wrap, 
            auto_ack=True)

        # 此时由listener接管连接释放
        listener = _Listener(chan)

        old = self.listen_map.get(queue_name)
        if old:
            old.stop()

        self.listen_map[queue_name] = listener

        listener.start()
