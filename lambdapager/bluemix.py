"""
_bluemix_

Create a lambdapager application for Bluemix or
other Cloudfoundry platform to run the pager on a timer.
"""
from lambdapager import LambdaPager


APP_MODULE = (
"""
import datetime
from time import sleep

from lambdapager import LambdaPager

CONFIG = {0}


def main():
    lp = LambdaPager(config_dict=CONFIG)
    delta = datetime.timedelta(seconds=int(lp.config['pager']['interval']))
    next_run = datetime.datetime.utcnow() + delta

    while True:
        if datetime.datetime.utcnow() < next_run:
            sleep(1)
        else:
            lp.run()
            next_run = next_run + delta

if __name__ == '__main__':
    main()
"""
)

MANIFEST_YML = (
"""
applications:
- name: lambdapager
  memory: 128M
  instances: 1
  no-route: true
  command: python lambdapager_bluemix.py
  path: .
"""
)

def create_bluemix_app():
    """
    Write Bluemix application script and manifest.yml file
    """
    lp = LambdaPager()


    with open('lambdapager_bluemix.py','w') as app:
        app.write(APP_MODULE.format(lp.config))

    with open('manifest.yml','w') as manifest:
        manifest.write(MANIFEST_YML.format(lp.config))


if __name__ == '__main__':
    create_bluemix_app()
