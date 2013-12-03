import random
import time
import string


def random_str(length=10):
    return ''.join(
        random.choice(string.ascii_uppercase) for i in range(length)
    )


random.seed(time.time())
N = 32
TEST_DOMAIN = (
    ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(N)) + ".foo.bar.test_domain.lab1.mozilla.net"
)
TEST_FQDN = "testfqdn." + TEST_DOMAIN
TEST_IPv4 = lambda: "10.1.2." + str(random.randint(0, 255))
TEST_IPv6 = lambda: "1234:1234::1" + str(random.randint(0, 255))
TEST_DESCRIPTION = '"This is a description"'
TEST_TTL = "9999"
TEST_PORT = "8888"
TEST_WEIGHT = "7777"
TEST_PRIORITY = "5555"
TEST_TEXT = "FOO 'BAR' baz"
TEST_INAME = lambda prefix='eth': prefix + str(random.randint(0, 255))
TEST_MAC = lambda: '{0}{0}:{1}{1}:{2}{2}:{3}{3}:{4}{4}:{5}{5}'.format(
    random.randint(0, 9),
    random.randint(0, 9),
    random.randint(0, 9),
    random.randint(0, 9),
    random.randint(0, 9),
    random.randint(0, 9)
)
TEST_NAME = lambda: 'whap{0}{1}foo'.format(
    random.randint(0, 255), random.randint(0, 255)
)
TEST_NETWORK = '10.0.{0}.{1}/27'.format(
    random.randint(0, 255), random.randint(0, 255)
)

TEST_STR = lambda: random_str()
