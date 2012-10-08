from string import Template
import pdb


# Knobs
ip_just = 40
pk_just = 10
name_just = 40
type_just = 15
class_just = 10
prio_just = 3
data_just = 1
extra_just = 3

def render_record(template, show_pk, **kwargs):
    if show_pk:
        prefix = str(kwargs['pk']).ljust(pk_just)
    else:
        prefix = ""
    return prefix + template.format(**kwargs)

def extract_ttl(d):
    if d['ttl'] == 3600 or d['ttl'] is None:
        ttl = ''
    else:
        ttl = str(ptr['ttl'])
    return ttl

def render_ptr(ptr_set, show_pk=True):
    """
    name ttl  class   rr     name
    """
    BUILD_STR = ''
    template = Template("{ip:$ip_just} {ttl} {rclass:$class_just} {rtype:$type_just} {name:1}.\n")
    template = template.substitute(ip_just=ip_just, class_just=class_just,
                        type_just=type_just)
    for ptr in ptr_set:
        ttl = extract_ttl(ptr)
        if show_pk:
            prefix = "{0}".format(ptr['pk']) + " " * pk_just
        else:
            prefix = ""
        BUILD_STR += render_record(template, show_pk, pk=ptr['pk'], ip=ptr['ip_str'], ttl=ttl, rclass='IN',
                rtype='PTR', name=ptr['name'])
    return BUILD_STR

def render_intr(interface_set, show_pk=True):
    """
    name  ttl  class   rr     ip
    """
    BUILD_STR = ''
    template = Template("{name:$name_just} {ttl} {rclass:$class_just} {rtype:$type_just} {address:$data_just}\n")
    template = template.substitute(name_just=name_just, class_just=class_just,
                        type_just=type_just, data_just=data_just)
    for rec in intr:
        if rec['ip_type'] == '4':
            rec_type = 'INTR (A/PTR)'
        else:
            rec_type = 'INTR (AAAA/PTR)'
        ttl = extract_ttl(rec)
        name = rec['meta']['fqdn'] + '.'
        BUILD_STR += render_record(template, pk=rec['pk'], name=name, ttl=ttl, rclass='IN',
                rtype=rec_type, address=rec['ip_str'])
    return BUILD_STR

def render_mx(mx_set, show_pk=True):
    """
    name           ttl  class   rr  pref name
    """
    BUILD_STR = ''
    template = Template("{name:$name_just} {ttl} {rclass:$class_just} {rtype:$type_just} {prio:$prio_just} {server:$data_just}.\n")
    template = template.substitute(name_just=name_just, class_just=class_just,
                type_just=type_just, prio_just=prio_just, data_just=data_just)
    for mx in mx_set:
        ttl = extract_ttl(mx)
        #name = mx.fqdn + '.' if mx.label != '' else '@'
        name = mx['meta']['fqdn'] + '.'
        BUILD_STR += render_record(template, show_pk, pk=mx['pk'], name=name, ttl=ttl, rclass='IN',
                rtype='MX', prio=str(mx['priority']), server=mx['server'])
    return BUILD_STR

def render_ns(nameserver_set, show_pk=True):
    """
    name           ttl  class   rr     name
    """
    BUILD_STR = ''
    template = Template("{name:$name_just} {ttl} {rclass:$class_just} {rtype:$type_just} {server:$data_just}.\n")
    template = template.substitute(name_just=name_just, class_just=class_just,
                        type_just=type_just, data_just=data_just)
    for ns in nameserver_set:
        ttl = extract_ttl(ns)
        BUILD_STR += render_record(template, show_pk, pk=ns['pk'], name=ns['domain'] + ".", ttl=ttl, rclass='IN', rtype='NS', server=ns['server'])
    return BUILD_STR

def render_address_record(addressrecord_set, show_pk=True):
    """
    name  ttl  class   rr     ip
    """
    BUILD_STR = ''
    template = Template("{name:$name_just} {ttl} {rclass:$class_just} {rtype:$type_just} {address:$data_just}\n")
    template = template.substitute(name_just=name_just, class_just=class_just,
                        type_just=type_just, data_just=data_just)
    for rec in addressrecord_set:
        ttl = extract_ttl(rec)
        if rec['ip_type'] == '4':
            rec_type = 'A'
        else:
            rec_type = 'AAAA'
        name = rec['meta']['fqdn'] + '.'
        BUILD_STR += render_record(template, show_pk, pk=rec['pk'], name=name, ttl=ttl, rclass='IN',
                rtype=rec_type, address=rec['ip_str'])
    return BUILD_STR

def render_cname(cname_set, show_pk=True):
    """
    name  ttl  class   rr     canonical name
    """
    BUILD_STR = ''

    template = Template("{name:$name_just} {ttl} {rclass:$class_just} {rtype:$type_just} {target:$data_just}.\n")
    template = template.substitute(name_just=name_just, class_just=class_just,
                        type_just=type_just, data_just=data_just)
    for cname in cname_set:
        ttl = extract_ttl(cname)

        name = cname['meta']['fqdn'] + '.'
        BUILD_STR += render_record(template, show_pk, pk=cname['pk'], name=name, ttl=ttl, rclass='IN',
                rtype='CNAME', target=cname['target'])
    return BUILD_STR

def render_srv(srv_set, show_pk=True):
    """
    srvce.prot.name  ttl  class   rr  pri  weight port target
    """
    BUILD_STR = ''
    template = Template("{name:$name_just} {ttl} {rclass:$class_just} {rtype:$type_just} {prio:$prio_just} {weight:$extra_just} {port:$extra_just} {target:$extra_just}.\n")
    template = template.substitute(name_just=name_just, class_just=class_just,
                        type_just=type_just, prio_just=prio_just, extra_just=extra_just)
    for srv in srv_set:
        ttl = extract_ttl(srv)
        name = srv['meta']['fqdn'] + '.'
        if srv['target'] == ".":
            target = ""  # There is already a trailing '.' in the template
        else:
            target = srv['target']
        BUILD_STR += render_record(template, show_pk, pk=srv['pk'], name=name, ttl=ttl, rclass='IN', rtype='SRV',
                prio=str(srv['priority']), weight=str(srv['weight']),
                port=str(srv['port']), target=target)
    return BUILD_STR

def render_txt(txt_set, show_pk=True):
    """
    name  ttl  class   rr     text
    """
    BUILD_STR = ''

    template = Template("{name:$name_just} {ttl} {rclass:$class_just} {rtype:$type_just} \"{data:$data_just}\"\n")
    template = template.substitute(name_just=name_just, class_just=class_just,
                        type_just=type_just, data_just=data_just)
    for txt in txt_set:
        ttl = extract_ttl(txt)
        name = txt['meta']['fqdn'] + '.'
        BUILD_STR += render_record(template, show_pk, pk=txt['pk'], name=name, ttl=ttl, rclass='IN', rtype='TXT', data=txt.txt_data)
    return BUILD_STR

def render_sshfp(sshfp_set, show_pk=True):
    BUILD_STR = ''

    template = Template("{name:$name_just} {ttl} {rclass:$class_just} "
            "{rtype:$type_just} {algorithm_number} {fingerprint_type} {key:$data_just}\n")
    template = template.substitute(name_just=name_just, class_just=class_just,
                        type_just=type_just, data_just=data_just)
    for sshfp in sshfp_set:
        ttl = extract_ttl(sshfp)
        name = sshfp['meta']['fqdn'] + '.'
        BUILD_STR += render_record(template, show_pk, pk=sshfp['pk'], name=name, ttl=ttl, rclass='IN', rtype='TXT',
                algorithm_number=sshfp.algorithm_number,
                fingerprint_type=sshfp.fingerprint_type,
                key=sshfp.key)
    return BUILD_STR
