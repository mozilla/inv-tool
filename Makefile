MANNAME="invtool"
MANTARGET="./docs/invtool"
RSTMAN="./docs/invtool.man.rst"
OPTIONS="--date"
INVTOOLPATH=./invtool
INVTOOLBIN=./bin/inv
SHELL_CONFIG=~/.zshrc

do_tests:
	python $(INVTOOLPATH)/tests/cli_tests.py
	python $(INVTOOLPATH)/tests/search_tests.py
	python $(INVTOOLPATH)/tests/kv_tests.py

view-docs:
	rst2man $(OPTIONS) $(RSTMAN) > $(MANTARGET).1
	gzip $(MANTARGET).1
	rm -rf ./docs/man1
	mkdir ./docs/man1
	mv $(MANTARGET).1.gz ./docs/man1/
	cd ./docs/ && man -M ./ $(MANNAME) ; cd ..

man:
	cd ./docs/ && man -M ./ $(MANNAME) ; cd ..

doc:
	rst2man $(OPTIONS) $(RSTMAN) > $(MANTARGET).1
	gzip $(MANTARGET).1
	rm -rf ./docs/man1
	mkdir ./docs/man1
	mv $(MANTARGET).1.gz ./docs/man1/

inspect:
	$(INVTOOLBIN) search -q "testfqdn"

install:
	sudo python setup.py install
	source $(SHELL_CONFIG)

clean:
	rm -rf ./docs/man1

VE:
	virtualenv test-invtool

destroy-VE:
	rm -rf test-invtool

uninstall:
	sudo rm -rf /usr/lib/python2.7/site-packages/invtool
	sudo rm -f /usr/bin/invtool
	sudo rm -f /usr/lib/python2.7/site-packages/Mozilla_Inventory_Tool-0.1.0-py2.7.egg-info
	sudo rm -f /etc/invtool.conf
