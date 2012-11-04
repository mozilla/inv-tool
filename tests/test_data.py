from gettext import gettext as _
import random
import time
import string
random.seed(time.time())
N = 10
TEST_DOMAIN =_(''.join(random.choice(string.ascii_uppercase + string.digits) for
                x in range(N)) + ".foo.bar.test_domain.scl3.mozilla.com")
TEST_FQDN = "testfqdn."+TEST_DOMAIN
TEST_IP = "10.1.2.3"
TEST_COMMENT = '"This is a comment"'
TEST_TTL = "9999"
