import time
import pika

from downloader.config.logging import logger
from downloader.domain.download.services import execute_download
from downloader.config.settings import env

parameters = pika.ConnectionParameters(
    host=env.RABBIT_HOST,
)


def reconnect():
    while True:
        try:
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            logger.error("Connection failed, retrying...")
            time.sleep(5)


def on_download_queue_message(ch, method, properties, body):
    try:
        message = body.decode("utf-8")
        logger.info(f"Download request for job of id: [{message}]")
        execute_download(int(message))
    except Exception as ex:
        logger.error(f"INTERNAL ERROR: {ex}")


def consume_downloader_queue():
    try:
        connection = reconnect()
        channel = connection.channel()

        channel.exchange_declare(
            exchange="stalkers", exchange_type="topic", durable=True
        )

        channel.queue_declare(
            queue="queue.novel.downloader",
            durable=True,
            arguments={"x-queue-type": "quorum"},
        )

        channel.queue_bind(
            exchange="stalkers",
            queue="queue.novel.downloader",
            routing_key="rk.novel.downloader",
        )

        channel.basic_consume(
            queue="queue.novel.downloader",
            on_message_callback=on_download_queue_message,
            auto_ack=True,
        )

        logger.info("[*] Waiting for messages. To exit press CTRL+C")

        channel.start_consuming()
    except pika.exceptions.ConnectionClosedByBroker:
        consume_downloader_queue()
