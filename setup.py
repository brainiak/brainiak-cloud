from setuptools import setup, find_packages

setup(
    name='brainiak-cloud',
    version='0.0.2',
    install_requires=[
        'click',
        'clickutil',
        'ipython',
        'requests',
        'pathos',
        'tqdm',
        'watchdog',
        'flask',
        'flask_session',
        'binaryornot',
        'cfncluster',
        'matplotlib',
        'pandas',
        'nilearn',
        'numpy',
        'scipy==1.10.0',  # See https://github.com/scipy/scipy/pull/8082
        'pybind11',
        'cython',
        'pika',
        'brainiak',
        'ipywidgets',
        'jupyter_contrib_nbextensions',
        'jupyter'
    ],
    author='Princeton Neuroscience Institute and Intel Corporation',
    author_email='dsuo@princeton.edu',
    url='https://github.com/brainiak/brainiak-cloud',
    description='Brain Imaging Analysis Kit Cloud',
    license='Apache 2',
    keywords='neuroscience, algorithm, fMRI, distributed, scalable',
    packages=find_packages(),
    python_requires='>=3.4',
    scripts=[
        'bin/client/notebook',
        'bin/client/watch',
        'bin/server/serve',
        'bin/client/copy'
    ]
)
