test:
	python tests/cli_tests.py
	python tests/search_tests.py

inspect:
	./bin/invdns search -q "testfqdn" | awk '{ print "./bin/invdns " $5  " delete --pk " $1}'

