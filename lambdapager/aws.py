"""
_aws_

Create a handler zip package for AWS lambda given
a configuration file.

The generated handler function is lambdapager_aws.handler and
the AWS deployment package is lambdapager_aws.zip.
"""
import os
import uuid
import zipfile
import shutil

import pip

from lambdapager import LambdaPager

WORKING_DIR = 'tmp-aws-{0}'.format(uuid.uuid1())

HANDLER_MODULE = (
"""
from lambdapager import LambdaPager

CONFIG = {0}


def handler(event, context):
    lp = LambdaPager(config_dict=CONFIG)
    lp.run()
"""
)


def create_aws_handler():
    """
    Create an AWS Lambda deployment package (PKZIP) given
    a config file 'lambdapager.conf' in the current working
    directory.

    This function will create a temporary directory in the
    working directory, build a zip archive in the temp
    directory, move it back to the working directory, and
    then delete the temporary directory.
    """
    lp = LambdaPager()

    os.mkdir(WORKING_DIR)
    pip.main([
        'install',
        '--find-links=dist/', # remove after uploading to pip
        '--no-cache-dir', # remove after uploading to pip
        'LambdaPager',
        '-t',
        WORKING_DIR
    ])
    os.chdir(WORKING_DIR)

    with open('lambdapager_aws.py','w') as handler:
        handler.write(HANDLER_MODULE.format(lp.config))

    with zipfile.ZipFile('lambdapager_aws.zip', 'w') as archive:
        working_path = os.getcwd()
        for root, dirs, files in os.walk(working_path):
            for f in files:
                if not f.endswith('zip'):
                    rel_dir = os.path.relpath(root, working_path)
                    archive.write(os.path.join(rel_dir, f))

    shutil.move(
        'lambdapager_aws.zip',
        os.path.join(os.pardir, 'lambdapager_aws.zip')
    )
    os.chdir(os.pardir)
    shutil.rmtree(WORKING_DIR)


if __name__ == '__main__':
    create_aws_handler()
