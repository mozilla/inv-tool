MANNAME="invtool"
MANTARGET="./docs/invtool"
RSTMAN="README.txt"
OPTIONS="--date"
INVTOOLPATH="./invtool"

do_tests:
	python $(INVTOOLPATH)/tests/cli_tests.py
	python $(INVTOOLPATH)/tests/search_tests.py

view-docs:
	rst2man $(OPTIONS) $(RSTMAN) > $(MANTARGET).1
	gzip $(MANTARGET).1
	rm -rf ./docs/man1
	mkdir ./docs/man1
	mv $(MANTARGET).1.gz ./docs/man1/
	cd ./docs/ && man -M ./ $(MANNAME) ; cd ..

docs:
	rst2man $(OPTIONS) $(RSTMAN) > $(MANTARGET).1
	gzip $(MANTARGET).1
	rm -rf ./docs/man1
	mkdir ./docs/man1
	mv $(MANTARGET).1.gz ./docs/man1/

inspect:
	$(INVTOOLPATH)/bin/invtool search -q "testfqdn"

clean:
	rm -rf ./docs/man1
