#!/usr/bin/env python
import simplejson as json
import shlex
import io
import requests

from invtool.main import do_dispatch
from invtool.lib.config import REMOTE, auth


class BAError(Exception):
    def __init__(self, error=None):
        self.error = error
        return super(BAError, self).__init__()


def ba_gather_vlan_pools(site, vlan_name, vlan_number, ip_type='4'):
    """
    This function should phone home to inventory and pull down a list of ip
    ranges.
    """
    tmp_url = "/en-US/bulk_action/gather_vlan_pools/"
    url = "{0}{1}".format(REMOTE, tmp_url)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {
        'vlan_name': vlan_name,
        'vlan_number': vlan_number,
        'site_name': site,
        'ip_type': ip_type
    }

    resp = requests.get(url, params=data, headers=headers, auth=auth())
    json_resp = json.loads(resp.content)
    if 'errors' in json_resp:
        return None, json_resp['errors']
    assert 'free_ranges' in json_resp, (
        "Something is broken. 'free_ranges' was not returen by Inventory"
    )
    return json_resp['free_ranges'], None


def ba_gather_range_pool(ip_range):
    resp, errors = ba_gather_ip_pool(ip_range)
    if errors:
        return resp, errors
    return resp['free_ranges'], None


def ba_gather_ip_pool(ip_range):
    command = '--json search --display-integers --range {0}'.format(ip_range)
    nas, (resp_code, resp_list) = do_dispatch(shlex.split(command))
    raw_json = '\n'.join(resp_list)
    if 'error_messages' in raw_json:
        return None, raw_json
    return json.loads(raw_json), None


def ba_export_systems_raw(search):
    command = 'ba_export --query {0}'.format(search)
    nas, (resp_code, resp_list) = do_dispatch(shlex.split(command))
    raw_json = '\n'.join(resp_list)
    if 'errors' in raw_json:
        return None, raw_json
    try:
        r = json.loads(raw_json)
    except ValueError:
        raise ValueError(
            "Couldn't decode from server. Response from server was: "
            "{0}".format(raw_json)
        )
    return r, None


def ba_export_systems_regex(search):
    """
    Export systems based on a regex search pattern. You can use
    https://inventory.mozilla.org/en-US/core/search/ to test out your regex.

    """
    return ba_export_systems_raw("/{search}".format(search=search))


def ba_export_systems_hostname_list(hostnames):
    """
    Export a list of systems by hostname.

    :param hostnames: A list of full hostnames that will be looked up in a
        single api call.
    :type hostnames: list

    """
    # Process the list STEP at a time
    def split_by_step(seq, STEP=100):
        while seq:
            yield seq[:STEP]
            seq = seq[STEP:]

    results = {'systems': {}}
    for chunk in list(split_by_step(hostnames)):
        search = '"{search}"'.format(
            search=' OR '.join(map(lambda h: "/^{h}$".format(h=h), chunk))
        )
        result, errors = ba_export_systems_raw(search)
        if errors:
            return None, errors
        results['systems'].update(result['systems'])
    return results, None


def ba_import(dict_blob, commit=False):
    """
    Import a blob of data. The data you pass in should have been originally
    exported via one of the ``ba_export`` functions.

    This function will convert the passed python dictionary into a JSON
    dictionary before sending it to Inventory to be processed.

    This function will return a dictionary and if that dictionary has the key
    'errors' then there were errors and nothing was saved during processing.

    :param dict_blob: A blob of data to import
    :type dict_blob: dict

    """
    if commit:
        dict_blob['commit'] = True
    json_blob = json.dumps(dict_blob)
    command = ['ba_import']
    if commit:
        command.append('--commit')
    with io.BytesIO(json_blob) as json_blob_fd:
        nas, (resp_code, resp_list) = do_dispatch(command, IN=json_blob_fd)
        raw_json = '\n'.join(resp_list)
        if 'errors' in raw_json:
            return None, raw_json
        try:
            resp = json.loads(raw_json)
        except ValueError:
            print raw_json
            return None, "Couldn't decode json from server"
        return resp, None


def removes_pk_attrs(blobs):
    """
    This function has sideaffects.
    """
    try:
        for blob in blobs:
            remove_pk_attrs(blob)
    except TypeError:
        remove_pk_attrs(blobs)


def remove_pk_attrs(blob):
    if isinstance(blob, dict):
        for s_blob in blob.values():
            s_blob.pop('pk', None)
            for attr, value in s_blob.iteritems():
                if attr == 'cname':  # CNAMEs are special
                    for i_blob in value:
                        i_blob.pop('pk', None)
                if isinstance(value, dict):
                    remove_pk_attrs(value)


def ba_export_system_template(hostname):
    template, error = ba_export_systems_hostname_list([hostname])
    if error:
        raise BAError(error=error)
    if len(template['systems']) != 1:
        raise BAError(error={
            'errors': 'The hostname for the system template you provided did '
            'not correspond to a single system'
        })
    system_template = template['systems']
    remove_pk_attrs(system_template)
    return system_template
