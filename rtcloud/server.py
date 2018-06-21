import os
import pickle
import sys
import subprocess
import platform

from pathos.helpers import mp

from werkzeug.utils import secure_filename
from flask import Flask, request, redirect
from flask_session import Session

from .utils import Logger
from .launcher import Launcher

from . import experiments


class Server:
    def __init__(self, opts):
        self.app = Flask(__name__)
        self.opts = opts

        self.BASE_URL = '/' + self.opts.get('BASE_URL')

        # Debug utilities
        self.logger = Logger()

        # Configure
        self.app.config['UPLOAD_FOLDER'] = self.opts.get('UPLOAD_FOLDER')
        self.ALLOWED_EXTENSIONS = set(self.opts.get('ALLOWED_EXTENSIONS'))

        # Initialize secrets
        # TODO: Add Config to handle secret data
        self.app.secret_key = 'super secret key'

        # Initialize session
        self.session = Session()
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.session.init_app(self.app)

        # Initialize routes
        self.app.add_url_rule(self.BASE_URL, '/', self.index, methods=['GET'])
        self.app.add_url_rule(os.path.join(
            self.BASE_URL,
            'start'
            ), 'start', self.start, methods=['POST'])
        self.app.add_url_rule(os.path.join(
            self.BASE_URL,
            'upload'
            ), 'upload', self.upload, methods=['POST'])

        if not self.opts.get('IGNORE_EXPERIMENT'):
            # Initialize experiment
            self.experimentClass = getattr(
                    experiments, self.opts.get('experimentClass'))
            self.experiment = self.experimentClass(self.opts)

        self.experimentOpts = None

        # Ready to roll
        self.app.debug = self.opts.get('DEBUG')
        self.app.run(host='0.0.0.0', port=self.opts.get('PORT'))

    def allowed_file(self, filename):
        # TODO: This is a crappy way to check extensions
        return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def index(self):
        return 'Hello, world!'

    def start(self):
        # print(request.form)
        self.experimentOpts = pickle.loads(request.get_data())
        self.logger.info('Starting experiment %s' %
                         self.experimentOpts['name'])

        # TODO: this is pretty terrible and I don't even bother joining
        process = mp.Process(target=Launcher, args=(
            self.experimentOpts['queue_work_name'],
            self.experimentOpts['queue_result_name'],
            self.experimentOpts.get('experiment_data'),
            ))
        process.start()
        return 'Successfully started!', 200

    # TODO: Have any semblance at all of error handling
    def upload(self):
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)

            path = os.path.join(
                    os.getcwd(),
                    self.app.config['UPLOAD_FOLDER']
                    )
            os.system('mkdir -p %s' % path)
            filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if not self.opts.get('IGNORE_EXPERIMENT'):
                return self.experiment.process(filepath), 202

            return 'Successfully queued!', 202
        return 'FAIL!'
