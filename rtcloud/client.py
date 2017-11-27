import os
import pickle
import time
import pathlib

import nibabel
import pika
import requests
from binaryornot.check import is_binary
from pathos.helpers import mp

from .ui import display_input, display_output


def get_paths(input_dir='.', extensions=['.nii.gz']):
    # Python checks path based on current working directory
    cwd = os.getcwd()
    os.chdir(input_dir)
    paths = [os.path.abspath(path) for path in os.listdir()]
    paths = filter(os.path.isfile, paths)
    paths = filter(lambda path: ''.join(
        pathlib.Path(path).suffixes) in extensions, paths)
    paths = list(paths)
    os.chdir(cwd)

    return paths


def get_channel(address, queue):
    rmq = pika.BlockingConnection(pika.ConnectionParameters(address))
    channel = rmq.channel()
    channel.queue_declare(queue=queue)

    return channel


def open_path(path):
    return open(path, 'r%s' % ('b' if is_binary(path) else ''))


class Client():
    def __init__(self, server_ip=None, conf=None, http_endpoint='brainiak',
                 server_port=21216, rmq_port=5672):
        assert server_ip is not None, 'server_address required'
        assert conf is not None, 'conf required'

        self.server_ip = server_ip
        self.server_port = server_port

        self.server_address = 'http://%s:%d' % \
            (self.server_ip, self.server_port)
        self.server_address = os.path.join(self.server_address, http_endpoint)

        self.rmq_port = rmq_port
        self.conf = conf
        self.connected = False
        self.name = 'rtcloud'
        self.queue_work_name = '%s_work' % self.name
        self.queue_result_name = '%s_result' % self.name

        self.conf['name'] = self.name
        self.conf['queue_work_name'] = self.queue_work_name
        self.conf['queue_result_name'] = self.queue_result_name

        if 'extensions' not in self.conf:
            self.conf['extensions'] = ['.nii.gz']

        # TODO: it'd be nice to have multiple queues, but not totally clear
        # based on quick inspection how we might select on multiple queues
        self.display_queue = mp.Queue()

        return

    def start(self):
        req = requests.post(os.path.join(self.server_address, 'start'),
                            data=pickle.dumps(self.conf))

        if req.status_code == 200:
            self.connected = True

        return

    def display(self):
        input_counter = 0
        output_counter = 0

        import matplotlib.pylab as plt

        f, axarr = plt.subplots(2, sharey=True)
        while True:
            result = self.display_queue.get()
            if result['src'] == 'input':
                input_counter += 1
                display_input(result['data'], input_counter, f, axarr[0])

            if result['src'] == 'output':
                output_counter += 1
                display_output(result['data'], output_counter, f, axarr[1])

    def queue(self, input_dir='.', tr=2000, loop=True, watch=False):
        assert self.connected, 'Not connected to server!'

        def queue_helper(display_queue, server_ip, queue_work_name, input_dir, tr, loop):
            # NOTE: Each process needs its own set of file descriptors
            channel = get_channel(server_ip, queue_work_name)
            paths = get_paths(input_dir, self.conf['extensions'])

            while True:
                for path in paths:
                    channel.basic_publish(
                        exchange='',
                        routing_key=queue_work_name,
                        body=pickle.dumps(nibabel.load(path).get_data())
                    )
                    display_queue.put({
                        'src': 'input',
                        'data': path
                    })
                    time.sleep(float(tr / 1000))
                if not loop:
                    break

        process = mp.Process(target=queue_helper, args=(
            self.display_queue,
            self.server_ip,
            self.queue_work_name,
            input_dir,
            tr,
            loop,
        ))

        process.start()

        return

    def upload(self, input_dir='.', tr=2000, loop=True, watch=False):
        assert self.connected, 'Not connected to server!'

        paths = get_paths(input_dir, self.conf['extensions'])

        for path in paths:
            req = requests.post(os.path.join(self.server_address, 'upload'),
                                files={'file': open_path(path)})

            # TODO: Fail gracefully
            assert req.status_code == 202

    def watch(self, callback=lambda *args: None):
        assert self.connected, 'Not connected to server!'
        print('Starting to watch!')

        def watch_helper(display_queue, server_ip, queue_result_name, callback):
            channel = get_channel(server_ip, queue_result_name)

            def callback_rmq(channel, method, properties, body):
                display_queue.put({
                    'src': 'output',
                    'data': body
                })
                callback(body)

            channel.basic_consume(
                callback_rmq,
                queue=queue_result_name,
                no_ack=True)
            channel.start_consuming()

        process = mp.Process(target=watch_helper, args=(
            self.display_queue,
            self.server_ip,
            self.queue_result_name,
            callback,
        ))

        process.start()

        return
