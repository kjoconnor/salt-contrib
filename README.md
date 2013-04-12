salt-contrib
============

My custom Salt grains/modules/etc.

ec2.py
======

A Salt grain to grab a whole bunch of EC2 info, right now it relies on your
system having an IAM role that can read EC2 data.  It can be easily modified
to rely on keys, but wasn't sure the best way to do that.  Forks welcomed!