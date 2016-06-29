# lambdapager

The stateless pager.

Copyright Eric Appelt, 2016, All Rights Reserved

[![Travs-CI status](https://travis-ci.org/appeltel/lambdapager.png)](https://travis-ci.org/appeltel/lambdapager)

### Introduction / FAQ

**What's it do?**

lambdapager works as an anonymous function somewhere in the cloud
that checks all the sites that you configured it to and then sends
SMS alerts to one or more configured numbers if the site is malfunctioning.

The idea is to set up some sort of timer/cron to run the function
every hour, day, etc...

**Who would use it?**

Students, hobbyists, people running small test or personal sites that don't
want to shell out around 10 bucks a month for a real full featured pager
service but want to save themselves the embarrasment/inconvenience of
having their site down without their knowledge.

**What are the requirements?**

A twilio account, some python 2.7 runtime on a server or hosted service that
can run on a timer. I'm working on some commands to simplify deployment to
things like Bluemix, AWS, Google Compute Engine, etc...

**Is python3 supported?**

Also in the TODO, I plan on using this little project as an exercise for
myself in slightly non-trivial 2/3 compatibility.

**How do I know that the lambdapager is still running?**

Also in the TODO, I plan on making a simple pagerpager. This would be a
tiny flask app that the lambdapager POSTs to that puts a heartbeat record
in a redis (or other) database, and another cron-like/timer function that
pages you if it hasn't gotten a heartbeat recently.

### Snarky FAQ

**How do I acknowledge a page?**

Lambdapager is stateless. Pages cannot be acknowledged, you will be
harassed until you fix your site.

**How do I go off duty?**

Lambdapager is stateless. Your shift is permanent and immutable.

**Can't one just disable the timer running the lambdapager?**

Look Dave, I can see you're really upset about this. I honestly think
you ought to sit down calmly, take a stress pill, and think things over.

# Installation, Configuration, and Usage

To install lambdapager clone this repository and use:

```
python setup.py sdist
pip install --no-index --find-links=dist/ LambdaPager
```

(Sorry, I'll put it on pip once it is a bit more mature)

This creates the `lambdapager` command which when invoked will look
for a file `lambdapager.conf` in the current working directory, check your
sites as configured, and page you if they are broken.

Here is an example configuration file:

```
[pager]
onduty = +12025550195, +12025550135

[twilio]
sid = 123ABC
token = 456DEF
number = +12025550113

[site-example]
url = https://www.my-website.com/
method = GET
status_codes = 200,202
response_contains = Hello, World

[site-example]
url = https://www.my-website.com/api/
method = POST
status_codes = 201
```

With this configuration, lambdapager will first test the endpoint
`https://www.my-website.com/` with a GET and expect a 200 or 202 response.
If the site is unavailable or a different status code is returned it will
send SMS messages to the two configured numbers in the "pager" section
from the account defined in the "twilio" section. Additionally,
the function will check that the strings "Hello" and "World" are contained
in the response body.

It will then check the second configured site `https://www.my-website.com/api/`
with a POST and expect a 201 response, or it will page.

# Deployment

Coming soon...
