'''
Management of AWS ELBs.
=======================

The AWS ELB module is used to make an instance either be present or
absent in a given ELB.

The default instance_id will be the minion's current ID.  Requires the 
ec2 grain in this repository.

.. code-block:: yaml

    MyLoadBalancer-Production:
      aws_elb.present:
        - instance_id: i-abc12345

    # This uses the current instance's ID
    MyLoadBalancer-Production:
      aws_elb.present

    MyLoadBalancer-Production:
      aws_elb.absent

'''

import logging

try:
    from boto.ec2 import elb as _boto_elb
    has_boto = 'aws_elb'
except ImportError:
    has_boto = False

log = logging.getLogger(__name__)

def __virtual__():
    '''
    Don't load if boto is not available
    '''

    return has_boto


def present(name, instance_id=None):
    '''
    Ensure that the given instance_id is present in the ELB

    name
        The name of the ELB instance to associate the instance with

    instance_id
        The instance_id to associate to the ELB.  Defaults to the current
        instance
    '''

    ret = {}

    if instance_id is None:
        try:
            instance_id = __grains__['instance_id']
        except KeyError:
            # We have no instance_id to act on
            ret = {'name': name,
                    'changes': {},
                    'result': False,
                    'comment': 'No instance ID was provided, and one ' \
                                'can not be gathered from grains.'}
            return ret

    elb = _get_elb(name=name)

    if not elb:
        ret = {'name': name,
                'changes': {},
                'result': False,
                'comment': 'Couldn\'t get ELB instance, are you sure you ' \
                            'have provided the correct name and you have ' \
                            'access to this part of the AWS API?'}

        return ret

    if instance_id in [x.id for x in elb.instances]:
        log.debug("Instance %s was already in ELB %s", instance_id, name)
        ret = {'name': name,
                'changes': {},
                'result': True,
                'comment': 'Instance %s was already in ELB %s' % \
                    (instance_id, name)}
        return ret

    if __salt__['aws_elb.present'](name=name, instance_id=instance_id):
        ret = {'name': name,
                'changes': {instance_id: 'present'},
                'result': True,
                'comment': 'Instance %s added to ELB %s' % \
                    (instance_id, name)}
    else:
        ret = {'name': name,
                'changes': {},
                'result': False,
                'comment': 'Failed to add instance %s to ELB %s' % \
                    (instance_id, name)}

    return ret

def absent(name, instance_id=None):
    '''
    Ensure that the given instance_id is absent from the ELB

    name
        The name of the ELB instance to disassociate the instance with

    instance_id
        The instance_id to disassociate from the ELB.  Defaults to the current
        instance
    '''

    ret = {}

    if instance_id is None:
        try:
            instance_id = __grains__['instance_id']
        except KeyError:
            # We have no instance_id to act on
            ret = {'name': name,
                    'changes': {},
                    'result': False,
                    'comment': 'No instance ID was provided, and one ' \
                                'can not be gathered from grains.'}
            return ret

    elb = _get_elb(name=name)

    if not elb:
        ret = {'name': name,
                'changes': {},
                'result': False,
                'comment': 'Couldn\'t get ELB instance, are you sure you ' \
                            'have provided the correct name and you have ' \
                            'access to this part of the AWS API?'}

        return ret

    if instance_id not in [x.id for x in elb.instances]:
        log.debug("Instance %s was already not in ELB %s", instance_id, name)
        ret = {'name': name,
                'changes': {},
                'result': True,
                'comment': 'Instance %s was already not in ELB %s' % \
                    (instance_id, name)}
        return ret

    if __salt__['aws_elb.absent'](name=name, instance_id=instance_id):
        ret = {'name': name,
                'changes': {instance_id: 'absent'},
                'result': True,
                'comment': 'Instance %s removed from ELB %s' % \
                    (instance_id, name)}
    else:
        ret = {'name': name,
                'changes': {},
                'result': False,
                'comment': 'Failed to remove instance %s from ELB %s' % \
                    (instance_id, name)}

    return ret


def _get_elb(name):
    '''
    Retrieves a boto ELB instance for the given name.

    '''
    try:
        elb_conn = _boto_elb.connect_to_region(__grains__['region'])
        elb = elb_conn.get_all_load_balancers(load_balancer_names=[name])
        log.debug('Got ELB instance %s' % elb)
    except Exception:
        import traceback
        log.debug("Error getting ELB instance %s", name)
        log.debug(traceback.format_exc())
        # TODO: Add support for using AWS keys. Right now you need IAM roles
        return False

    log.debug('Returning ELB instance %s', elb)
    return elb[0]