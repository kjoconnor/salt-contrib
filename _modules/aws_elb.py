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
    Add an instance to the given ELB.  Requires 'instance_id' to be given or
    be part of the minion's grains.

    CLI Example:

        salt '*' aws_elb.present MyLoadBalancer-Production

        salt '*' aws_elb.present MyLoadBalancer-Production i-89393af9
    '''

    if instance_id is None:
        try:
            instance_id = __grains__['instance_id']
        except KeyError:
            return False

    elb = _get_elb(name)

    try:
        elb.register_instances([instance_id])
    except Exception:
        import traceback
        log.debug("Error registering instance %s", instance_id)
        log.debug(traceback.format_exc())
        return False

    log.debug("Successfully added instance %s to ELB %s",
        instance_id,
        name
    )
    return True

def absent(name, instance_id=None):
    '''
    Removes an instance from the given ELB.  Requires 'instance_id' to be
    given or be part of the minion's grains.

    CLI Example:

        salt '*' aws_elb.absent MyLoadBalancer-Production

        salt '*' aws_elb.absent MyLoadBalancer-Production i-89393af9
    '''

    if instance_id is None:
        try:
            instance_id = __grains__['instance_id']
        except KeyError:
            return False

    elb = _get_elb(name)

    try:
        elb.deregister_instances([instance_id])
    except Exception:
        import traceback
        log.debug("Error deregistering instance %s", instance_id)
        log.debug(traceback.format_exc())
        return False

    log.debug("Successfully removed instance %s from ELB %s",
        instance_id,
        name
    )

    return True


def _get_elb(name):
    '''
    Retrieves a boto ELB instance for the given name.

    '''
    try:
        elb_conn = _boto_elb.connect_to_region(__grains__['region'])
        elb = elb_conn.get_all_load_balancers(load_balancer_names=[name])
    except Exception:
        # TODO: Add support for using AWS keys. Right now you need IAM roles
        import traceback
        log.debug("Error getting ELB instance %s", name)
        log.debug(traceback.format_exc())
        return False

    return elb[0]