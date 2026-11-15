import signal
import time
from multiprocessing import Pool

import pika

from downloader.config.logging import logger
from downloader.config.settings import env
from downloader.domain.download.services import execute_download

parameters = pika.ConnectionParameters(
    host=env.RABBIT_HOST,
)


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


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
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as ex:
        logger.error(f"INTERNAL ERROR: {ex}")


def download_consumer(position: int):
    try:
        connection = reconnect()
        channel = connection.channel()

        channel.basic_qos(prefetch_count=1)

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
            auto_ack=False,
        )

        logger.info(f"[*] Worker {position} waiting for messages. To exit press CTRL+C")

        channel.start_consuming()
    except pika.exceptions.ConnectionClosedByBroker:
        download_consumer()


def start_workers(workers_count: int = 5):
    with Pool(processes=workers_count, initializer=init_worker) as pool:
        try:
            pool.map(download_consumer, [i + 1 for i in range(workers_count)])
        except KeyboardInterrupt:
            print("\n")
            pool.terminate()
            pool.join()
