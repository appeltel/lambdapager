#!/usr/bin/env python

from distutils.core import setup

setup(
    name='LambdaPager',
    version='0.0.0',
    description='The stateless pager!',
    author='Eric Appelt',
    author_email='eric.appelt@gmail.com',
    url='https://github.com/appeltel/lambdapager',
    packages=['lambdapager'],
    entry_points={'console_scripts': [
        'lambdapager = lambdapager.__main__:main',
        'lambdapager_bluemix_create = lambdapager.bluemix:create_bluemix_handler',
        'lambdapager_aws_create = lambdapager.aws:create_aws_handler'
    ]},
    install_requires=['requests>=2.10.0', 'twilio>=5.4.0'],
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring'
    )
)
