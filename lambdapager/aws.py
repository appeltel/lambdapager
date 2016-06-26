"""
_aws_

Create a handler module for AWS lambda given
a configuration file.

The generated handler function is lambdapager_aws.handler

Eventually this should create a full AWS deployment zip file
"""
from lambdapager import LambdaPager

HANDLER_MODULE = (
"""
from lambdapager import LambdaPager

CONFIG = {0}


def handler(event, context):
    lp = LambdaPager(config=CONFIG)
    lp.run()
"""
)


def create_aws_handler():
    lp = LambdaPager()
    with open('lambdapager_aws.py','w') as handler:
        handler.write(HANDLER_MODULE.format(lp.config))


if __name__ == '__main__':
    create_aws_handler()
