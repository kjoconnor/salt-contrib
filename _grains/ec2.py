import json
import logging
import requests

try:
    from boto.ec2 import connect_to_region as _connect_to_region
    has_boto = True
except ImportError:
    has_boto = False

logger = logging.getLogger(__name__)

def _get_item(url, root='http://169.254.169.254/latest/meta-data/'):
    r = requests.get('%s%s' % (root, url))

    if r.status_code == requests.codes.ok:
        return r.text

def _ec2_metadata():
    grains = {}

    grains['ami_id'] = _get_item('ami-id')
    grains['hostname'] = _get_item('hostname')
    grains['instance_id'] = _get_item('instance-id')
    grains['instance_type'] = _get_item('instance-type')
    grains['local_ipv4'] = _get_item('local-ipv4')
    grains['mac'] = _get_item('mac')
    grains['availability_zone'] = _get_item('placement/availability-zone')
    grains['public_hostname'] = _get_item('public-hostname')
    grains['public_ipv4'] = _get_item('public-ipv4')


    iam_role = json.loads(_get_item('iam/info'))
    grains['iam_role'] = iam_role['InstanceProfileArn'].split('/')[1]

    instance_identity = json.loads(_get_item(
                                        url='dynamic/instance-identity/document',
                                        root='http://169.254.169.254/latest/')
                                    )

    grains['architecture'] = instance_identity['architecture']
    grains['region'] = instance_identity['region']
    grains['account'] = instance_identity['accountId']

    return grains

def _ec2_api_data(instance_id, region='us-east-1'):
    if has_boto is not True:
        return {}

    conn = _connect_to_region(region)

    reservation = conn.get_all_instances(filters={'instance-id': instance_id})
    for instance in reservation[0].instances:
        if instance.id == instance_id:
            found_instance = instance

    grains = {}

    grains['tags'] = found_instance.tags.copy()
    grains['key_name'] = found_instance.key_name
    grains['launch_time'] = found_instance.launch_time
    grains['security_groups'] = [item.name for item in found_instance.groups]

    return grains


def ec2_info():
    metadata_grains = _ec2_metadata()
    
    api_grains = _ec2_api_data(
                            instance_id=metadata_grains['instance_id'],
                            region=metadata_grains['region']
                        )

    override_grains = {'ec2_instance': True}

    return dict(
        metadata_grains.items() +
        api_grains.items() +
        override_grains.items()
    )