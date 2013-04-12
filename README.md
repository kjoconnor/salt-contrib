salt-contrib
============

My custom Salt grains/modules/etc.

_grains/ec2.py
======

A Salt grain to grab a whole bunch of EC2 info, right now it relies on your
system having an IAM role that can read EC2 data.  It can be easily modified
to rely on keys, but wasn't sure the best way to do that.  Forks welcomed!

_modules/aws_elb.py / _states/aws_elb.py
=========================================
A state/module to add instances to an existing ELB instance.