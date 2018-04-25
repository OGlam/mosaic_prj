"""Setup opendkim and approve host.
See https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-dkim-with-postfix-on-debian-wheezy
"""

from fabric.api import task, sudo, cd
from fabric.contrib.files import append, comment, env


@task
def setup_postfix():
    comment("/etc/postfix/main.cf", "^smtpd_use_tls=yes$", use_sudo=True)
    append("/etc/postfix/main.cf", [
        "smtp_tls_security_level=may",
        "smtpd_tls_security_level=may",
    ], use_sudo=True)
    sudo("service postfix restart")


OPENDKIM_OPTIONS = """
AutoRestart Yes
AutoRestartRate 10/1h
UMask 002
Syslog yes
SyslogSuccess Yes
LogWhy Yes
Canonicalization relaxed/simple
ExternalIgnoreList refile:/etc/opendkim/TrustedHosts
InternalHosts refile:/etc/opendkim/TrustedHosts
KeyTable refile:/etc/opendkim/KeyTable
SigningTable refile:/etc/opendkim/SigningTable
Mode sv
PidFile /var/run/opendkim/opendkim.pid
SignatureAlgorithm rsa-sha256
UserID opendkim:opendkim
Socket inet:12301@localhost
"""


def setup_opendkim_general():
    lines = OPENDKIM_OPTIONS.strip().splitlines()
    append("/etc/opendkim.conf", lines, use_sudo=True)

    comment("/etc/default/opendkim", 'SOCKET=local:$RUNDIR/opendkim.sock',
           use_sudo=True)

    append("/etc/default/opendkim", 'SOCKET="inet:12301@localhost"',
           use_sudo=True)

    sudo('/lib/opendkim/opendkim.service.generate')
    sudo('systemctl daemon-reload')

    lines = [
        "milter_protocol = 2",
        "milter_default_action = accept",
        "smtpd_milters = inet:localhost:12301",
        "non_smtpd_milters = inet:localhost:12301",
    ]
    append("/etc/postfix/main.cf", lines, use_sudo=True)

    sudo("mkdir -pv /etc/opendkim/keys")

    lines = [
        "127.0.0.1",
        "localhost",
    ]
    append("/etc/opendkim/TrustedHosts", lines, use_sudo=True)


def setup_opendkim_host(host):
    sudo("mkdir -pv /etc/opendkim/keys")

    append("/etc/opendkim/TrustedHosts", host, use_sudo=True)

    s = "mail._domainkey.{0} {0}:mail:/etc/opendkim/keys/{0}/mail.private".format(
        host)
    append("/etc/opendkim/KeyTable", s, use_sudo=True)

    s = "*@{0} mail._domainkey.{0}".format(host)
    append("/etc/opendkim/SigningTable", s, use_sudo=True)

    d = "/etc/opendkim/keys/{}".format(host)
    sudo('mkdir -pv {}'.format(d))
    with cd(d):
        sudo("opendkim-genkey -s mail -d {}".format(host))
        sudo("chown opendkim:opendkim mail.private")
        s = sudo("cat mail.txt", )

    sudo("systemctl restart postfix")
    sudo("systemctl restart opendkim")

    print("=================== OPENDKIM KEY START =================")
    print(s)
    print("=================== OPENDKIM KEY END ===================")


def _setup_opendkim(hosts):
    setup_opendkim_general()
    for host in hosts:
        setup_opendkim_host(host)


@task
def setup_opendkim():
    _setup_opendkim(env.hosts)

@task
def postfix_log():
    sudo('tail /var/log/mail.err /var/log/mail.log')

