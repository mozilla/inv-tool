#!/usr/bin/env python
from invtool.lib.ba import *  # noqa
import csv  # noqa


def export(csv):
    # Step 1 and Step 2.

    # This function grabs the system blob for the system with the given
    # hostname, removes all the 'pk' attributes, and returns a dictionary
    # representing the system.

    # Things to do before calling this function:
    # ==========================================
    # You should set a system up completely in the Inventory UI as if
    # all data for that system were available; create it with all Static
    # Registrations it will need, all Harware Adapters it will need, and all
    # KeyValue pairs. Do this even if this information is wrong (i.e. you use
    # 00:00:00:00:00:00 as the mac address) because this will help you in step
    # (3) when you set the correct information. If a peice of information is
    # common to all systems you are about to create (like operating system or
    # purchase date), this is the place to make sure that information is the
    # same for new systems.

    system_template = export_system_template(
        'node26.plum.metrics.phx1.mozilla.com'  # <~~~ Edit this hostname
    )

    # Step 3
    
    print system_template


def ba_modify(data):
    pass


def do_import(data):
    pass


def main():
    csv_file = '/home/juber/test.csv'  # <~~~ Edit this file path
    with open(csv_file, 'rb') as csvfile:
    export('')
    #if errors:
    #    print "Errors:"
    #    print errors
    #    return

    #print ba_import(export)

"""
Creating a lot of systems at the same time can be acheived by:

    1. Exporting a single system

    2. Removing the 'pk' attribute from every object in its JSON blob

    3. Making a bunch of copies of the blob, one for each system you need to
       create.

    4. For each new host you are creating (which usually corresponds to a
       single line in a CSV file) update a copied blob to contain the
       information specific to that host.

    5. Export the updated blob back to Inventory for saving


In step (1) you are essentially using a system as a template. 
In step (2) you should remove the 'pk' attribute for every JSON blob so
Inventory thinks you are creating, and not updating, objects when you send the
JSON to be imported. For this you can use the ``remove_pk_attrs()`` function.

Note::
    Because the template system is already created, remember to remove it from
    the list of objects you are sending to Invetory in step (5). If you forget
    to do this Inventory will complain about a 'duplicate hostname'.

In step (4) you should be using the data in the your CSV to update the JSON
blob you created in step (3).

Step (5) is sending the modified JSON blob to Inventory for processing. Make
sure you pay attention to the results sent back from Invenotry after this step
-- if there are errors with the data you sumbited, this is where the errors
will manifest.

"""

if __name__ == "__main__":
    main()
