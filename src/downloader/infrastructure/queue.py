import signal
import time
from multiprocessing import Pool

import pika
import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel

from downloader.config.logging import logger
from downloader.config.settings import env
from downloader.domain.download.services import execute_download

parameters = pika.ConnectionParameters(
    host=env.RABBIT_HOST,
    heartbeat=0,
)

MAX_RETRIES = 3
RETRY_DELAY_MS = 5000

MAIN_EXCHANGE = "stalkers"
RETRY_EXCHANGE = "stalkers.retry"
MAIN_QUEUE = "queue.novel.downloader"
RETRY_QUEUE = "novel.downloader.retry"
MAIN_RK = "rk.novel.downloader"
RETRY_RK = "rk.retry"


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def reconnect():
    while True:
        try:
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            logger.error("Connection failed, retrying...")
            time.sleep(5)


def get_retry_count(properties) -> int:
    headers = properties.headers or {}
    deaths = headers.get("x-death") or []
    return sum(
        d.get("count", 0)
        for d in deaths
        if d.get("queue") == MAIN_QUEUE and d.get("reason") == "rejected"
    )


def on_download_queue_message(ch: BlockingChannel, method, properties, body):
    try:
        message = body.decode("utf-8")
        logger.info(f"Download request for job of id: [{message}]")
        execute_download(int(message))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as ex:
        retries = get_retry_count(properties)
        if retries < MAX_RETRIES:
            logger.error(f"RETRY {retries + 1}/{MAX_RETRIES}: INTERNAL ERROR: {ex}")
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        else:
            logger.error(f"MAX RETRIES REACHED: INTERNAL ERROR: {ex}")
            ch.basic_ack(delivery_tag=method.delivery_tag)


def setup_topology(channel: BlockingChannel):
    channel.exchange_declare(exchange=MAIN_EXCHANGE, exchange_type="topic", durable=True)
    channel.exchange_declare(exchange=RETRY_EXCHANGE, exchange_type="topic", durable=True)

    channel.queue_declare(
        queue=MAIN_QUEUE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": RETRY_EXCHANGE,
            "x-dead-letter-routing-key": RETRY_RK,
        },
    )
    channel.queue_bind(queue=MAIN_QUEUE, exchange=MAIN_EXCHANGE, routing_key=MAIN_RK)

    channel.queue_declare(
        queue=RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": RETRY_DELAY_MS,
            "x-dead-letter-exchange": MAIN_EXCHANGE,
            "x-dead-letter-routing-key": MAIN_RK,
        },
    )
    channel.queue_bind(queue=RETRY_QUEUE, exchange=RETRY_EXCHANGE, routing_key=RETRY_RK)


def download_consumer(position: int):
    while True:
        try:
            connection = reconnect()
            channel = connection.channel()
            channel.basic_qos(prefetch_count=1)

            setup_topology(channel)
            channel.basic_consume(
                queue=MAIN_QUEUE,
                on_message_callback=on_download_queue_message,
                auto_ack=False,
            )

            logger.info(f"[*] Worker {position} waiting for messages. To exit press CTRL+C")
            channel.start_consuming()
        except pika.exceptions.AMQPError as ex:
            logger.error(f"Worker {position} lost connection: {ex}. Reconnecting...")
            time.sleep(5)


def start_workers(workers_count: int = 5):
    with Pool(processes=workers_count, initializer=init_worker) as pool:
        try:
            pool.map(download_consumer, [i + 1 for i in range(workers_count)])
        except KeyboardInterrupt:
            print("\n")
            pool.terminate()
            pool.join()