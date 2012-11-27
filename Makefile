MANTARGET="invdns"
RSTMAN="inv-tool.rst"
OPTIONS="--date"

do_tests:
	python tests/cli_tests.py
	python tests/search_tests.py

view-docs:
	rst2man $(OPTIONS) $(RSTMAN) > $(MANTARGET).1
	gzip $(MANTARGET).1
	rm -rf man1
	mkdir man1
	mv $(MANTARGET).1.gz man1/
	man -M ./ $(MANTARGET)

docs:
	rst2man $(OPTIONS) $(RSTMAN) > $(MANTARGET).1
	gzip $(MANTARGET).1
	rm -rf man1
	mkdir man1
	mv $(MANTARGET).1.gz man1/

inspect:
	./bin/invdns search -q "testfqdn"

clean:
	rm -rf man1
	rm -f $(MANTARGET).1
	rm -f $(MANTARGET).1.gz
