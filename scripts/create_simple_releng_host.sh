#!/bin/bash

# This is a sample script showing how you could use invtool to possibly automate the creation of hosts.

#INVTOOL='./inv'
#source ../env_invtool/bin/activate

set -e -x

function create_releng_host(){
    # This function will create a system, matching A/PTR, a CNAME, and DHCP info
    #
    # Params:
    #   $1 hostname:
    #       used for system hostname, A, PTR/CNAME target, and later DHCP option-hostname
    #   $2 ip  (used for A/PTR and later DHCP KeyValue stuff)
    #   $3 cname fqdn

    host_fqdn=$1
    ip=$2
    cname_fqdn=$3

    # In the next command we are going to create a system. Later, when we
    # create keyvalue pairs, we will want that system's pk. The --pk-only flag
    # will cause invtool to print *only* the pk of the object it just
    # created/updated
    system_pk=$(
        $INVTOOL --pk-only SYS create --hostname ${host_fqdn}
    )


    # {rint the system we just created (this is not required)
    $INVTOOL SYS detail --pk $system_pk


    # Create DNS records
    $INVTOOL A create --fqdn ${host_fqdn} --ip ${ip} --private
    $INVTOOL PTR create --ip ${ip} --target ${host_fqdn} --private
    $INVTOOL CNAME create --fqdn ${cname_fqdn} --target ${host_fqdn} --private

    # Create KeyValue with the following info
    nic_number=0
    mac=11:22:33:44:55:66
    option_hostname=${host_fqdn}
    dhcp_scope='scl3-vlan33-fake'
    create_kvs ${system_pk} ${nic_number} ${ip} ${mac} ${host_fqdn} ${dhcp_scope}
}

function create_kvs(){
    # Create Key Value pairs to bootstrap DHCP.

    # Right now DHCP is done via the keyvalue store (this will be changing), so
    # this is how we you can create key-value pairs associated with the system
    # we just created

    # Params:
    system_pk=$1
    nic_number=$2
    ip=$3
    mac=$4
    host_fqdn=$5
    dhcp_scope=$6
    $INVTOOL SYS_kv create --obj-pk $system_pk --key nic.${nic_number}.ipv4_address.0 --value ${ip}
    $INVTOOL SYS_kv create --obj-pk $system_pk --key nic.${nic_number}.mac_address.0 --value ${mac}
    $INVTOOL SYS_kv create --obj-pk $system_pk --key nic.${nic_number}.name.0 --value nic${nic_number}
    $INVTOOL SYS_kv create --obj-pk $system_pk --key nic.${nic_number}.option_hostname.name.0 --value ${host_fqdn}
    $INVTOOL SYS_kv create --obj-pk $system_pk --key nic.${nic_number}.dhcp_scope.name.0 --value ${dhcp_scope}
}

create_releng_host foo-test.mozilla.com 10.3.4.5 cname-foo.mozilla.org
