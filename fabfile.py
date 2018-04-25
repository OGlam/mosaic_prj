"""To use this file, create a `local_fabfile.py` with

    ADMIN_EMAIL="your@email.com"

"""

import datetime
import os
from io import StringIO
from pathlib import Path

from fabric import operations
from fabric.api import *
from fabric.contrib.console import confirm
from fabfile_postfix import setup_postfix, setup_opendkim, postfix_log
from fabfile_local import ADMIN_EMAIL

env.user = "sysop"
env.hosts = ["psifas.oglam.hasadna.org.il"]

env.app_name = "psifas"
env.wsgi_file = "mosaic_prj/wsgi.py"
env.stats_port = 9000
env.project = "psifas"
env.code_dir = f"/home/sysop/{env.project}"
env.clone_url = "https://github.com/yaniv14/mosaic_prj.git"

env.venv_name = env.project
env.venvs = f"/home/sysop/.virtualenvs/"
env.venv_path = f"{env.venvs}{env.venv_name}/"
env.venv_command = f"source {env.venv_path}/bin/activate"

env.backup_dir = f"{env.code_dir}/backup/"

AUTO_RENEW_SCRIPT = '/home/certbot/auto-renew.sh'


@task
def uptime():
    run("uptime")


APT_PACKAGES = [
    # generic system related packages
    'unattended-upgrades',  # for auto updating your system
    'ntp',  # To keep time synchromized
    'fail2ban',  # to secure against SSH/other attacks

    'postfix',  # mail server
    'opendkim',  # SSL for mail
    'opendkim-tools',

    # useful tools
    'git',
    'htop',
    'most',

    'python3',
    'virtualenvwrapper',  # for easily managing virtualenvs

    # required libraries for building some python packages
    'build-essential',
    'python3-dev',
    'libpq-dev',
    'libjpeg-dev',
    'libjpeg8',
    'zlib1g-dev',
    'libfreetype6',
    'libfreetype6-dev',
    'libgmp3-dev',

    # postgres database
    'postgresql',

    'nginx',  # a fast web server
    'uwsgi',  # runs python (django) apps via WSGI
    'uwsgi-plugin-python3',  # runs python (django) apps via WSGI

    'rabbitmq-server',  # for offline tasks via celery
]


@task
def apt_install():
    pkgs = " ".join(APT_PACKAGES)
    sudo(f"DEBIAN_FRONTEND=noninteractive apt install -y -q {pkgs}",
         pty=False)


@task
def apt_upgrade():
    sudo("DEBIAN_FRONTEND=noninteractive apt update -y", pty=False)
    sudo("DEBIAN_FRONTEND=noninteractive apt upgrade -y", pty=False)


@task
def create_postgres_su():
    run("sudo -u postgres createuser -s sysop")
    run("createdb sysop")


@task
def clone_project():
    run(f"git clone {env.clone_url} {env.code_dir}", pty=False)


@task
def create_venv():
    run(f"mkdir -p {env.venvs}")
    run(
        f"virtualenv -p /usr/bin/python3 --prompt='({env.venv_name}) ' {env.venv_path}")


from contextlib import contextmanager


@contextmanager
def virtualenv():
    with cd(env.code_dir):
        with prefix(env.venv_command):
            yield


@task
def upgrade_pip():
    with virtualenv():
        run("pip install --upgrade pip", pty=False)


@task
def lock_requirements():
    local("pipenv lock -r > requirements.txt")


@task
def pip_install():
    with virtualenv():
        run("pip install -r requirements.txt", pty=False)


@task
def m(cmd, pty=False):
    with virtualenv():
        run(f"./manage.py {cmd}", pty=pty)


@task
def check():
    m('check')


@task
def send_test_mail():
    m('sendtestemail --admin')


@task
def createsuperuser():
    m('createsuperuser', True)


@task
def git_pull():
    with virtualenv():
        run("git pull --ff-only", pty=False)


@task
def create_db():
    with virtualenv():
        run("./manage.py sqlcreate | psql", pty=False)


@task
def migrate():
    m('migrate --noinput')


UWSGI_CONF = """
[uwsgi]
plugin = python3
virtualenv = {env.venv_path}
chdir = {env.code_dir}
wsgi-file = {env.wsgi_file}
processes = 4
threads = 1
stats = 127.0.0.1:{env.stats_port}
"""


@task
def create_uwsgi_conf():
    conf = UWSGI_CONF.format(env=env)
    filename = f"/etc/uwsgi/apps-available/{env.app_name}.ini"
    enabled = f"/etc/uwsgi/apps-enabled/{env.app_name}.ini"
    put(StringIO(conf), filename, use_sudo=True, )
    sudo(f"ln -sf {filename} {enabled}")
    sudo("service uwsgi stop")
    sudo("service uwsgi start")


NGINX_CONF = """
ssl_ciphers         AES128-SHA:AES256-SHA:RC4-SHA:DES-CBC3-SHA:RC4-MD5;
ssl_session_cache   shared:SSL:10m;
ssl_session_timeout 10m;
ssl_certificate    /home/certbot/conf/live/{host}/fullchain.pem;
ssl_certificate_key /home/certbot/conf/live/{host}/privkey.pem;

server {{
   listen 80 default_server;
   return 404;
}}

server {{
    listen 80;
    server_name {host};
    return 301 https://{host}$request_uri;
}}

server {{
   listen 443 ssl default_server;
   return 404;
}}

server {{
    listen 443 ssl;
    server_name {host};
    charset     utf-8;

    location /.well-known/ {{
        root /home/certbot/webroot/;
    }}

    location /static/ {{
        alias {env.static_path};
    }}

    location / {{
        uwsgi_pass  unix://{env.uwsgi_socket};
        include     uwsgi_params;
    }}
}}"""

env.uwsgi_socket = f"/run/uwsgi/app/{env.app_name}/socket"
env.static_path = f"{env.code_dir}/collected-static/"


@task
def create_nginx_conf():
    conf = NGINX_CONF.format(
        host=env.hosts[0],
        env=env,
    )
    filename = f"/etc/nginx/sites-available/{env.app_name}.conf"
    enabled = f"/etc/nginx/sites-enabled/{env.app_name}.conf"
    put(StringIO(conf), filename, use_sudo=True, )
    sudo(f"ln -sf {filename} {enabled}")

    sudo("rm -vf /etc/nginx/sites-enabled/default")

    sudo("nginx -t")

    sudo("service nginx reload")


@task
def nginx_log():
    sudo("tail /var/log/nginx/error.log")


@task
def uwsgi_log(n=50):
    sudo(f"tail -n {n} /var/log/uwsgi/app/*.log")


@task
def collect_static():
    m('collectstatic --noinput')


@task
def reload_app():
    sudo('systemctl reload uwsgi.service')


@task
def upgrade():
    # stop_celery()
    git_pull()
    pip_install()
    migrate()
    collect_static()
    reload_app()
    # start_celery()


def make_backup():
    now = datetime.datetime.now()
    filename = now.strftime(
        "{}-%Y-%m-%d-%H-%M.sql.gz".format(env.app_name))
    run('mkdir -p {}'.format(env.backup_dir))
    fullpath = env.backup_dir + filename
    run('sudo -u postgres pg_dump --no-acl --no-owner {} | gzip > {}'.format(
        env.app_name,
        fullpath))
    return fullpath


@task
def remote_backup_db():
    path = make_backup()
    operations.get(path)
    run('ls -alh {}'.format(path))


@task
def backup_db():
    files = operations.get(make_backup())
    if len(files) != 1:
        print("no file downloaded!")
        return

    print(f"backup downloaded to: {files[0]}")
    latest = "latest.sql.gz"
    target = Path(files[0])
    local(f"cd {target.parent} && ln -fs {target} {latest}")
    print(f"link created to: {target.parent / latest}")
    return target


@task
def load_local_db_from_file(filename):
    if not os.path.isfile(filename):
        abort("Unknown file {}".format(filename))

    if not confirm(
            "DELETE local db and load from backup file {}?".format(filename)):
        abort("Aborted.")

    drop_command = "drop schema public cascade; create schema public;"
    local('''python3 -c "print('{}')" | python manage.py dbshell'''.format(
        drop_command, filename))

    cmd = "gunzip -c" if filename.endswith('.gz') else "cat"
    local('{} {} | python manage.py dbshell'.format(cmd, filename))


@task
def load_local_db_from_latest():
    filename = backup_db()
    load_local_db_from_file(str(filename))


env.celery_service = f'{env.app_name}_celery'

CELERY_SERVICE_FILE = r"""[Unit]
Description={env.project} Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory={env.code_dir}

Environment="CELERYD_NODES=w1"
Environment="CELERY_BIN={env.venv_path}bin/celery"
Environment="CELERY_APP={env.project}"
Environment="CELERYD_MULTI=multi"
Environment="CELERYD_OPTS=--time-limit=300 --concurrency=4"

# - %n will be replaced with the first part of the nodename.
# - %I will be replaced with the current child process index
#   and is important when using the prefork pool to avoid race conditions.
Environment="CELERYD_PID_FILE=/var/run/{env.celery_service}/%n.pid"
Environment="CELERYD_LOG_FILE=/var/log/{env.celery_service}/%n%I.log"
Environment="CELERYD_LOG_LEVEL=INFO"

ExecStart=/bin/sh -c '${{CELERY_BIN}} multi start ${{CELERYD_NODES}} \
  -A ${{CELERY_APP}} --pidfile=${{CELERYD_PID_FILE}} \
  --logfile=${{CELERYD_LOG_FILE}} --loglevel=${{CELERYD_LOG_LEVEL}} ${{CELERYD_OPTS}}'
ExecStop=/bin/sh -c '${{CELERY_BIN}} multi stopwait ${{CELERYD_NODES}} \
  --pidfile=${{CELERYD_PID_FILE}}'
ExecReload=/bin/sh -c '${{CELERY_BIN}} multi restart ${{CELERYD_NODES}} \
  -A ${{CELERY_APP}} --pidfile=${{CELERYD_PID_FILE}} \
  --logfile=${{CELERYD_LOG_FILE}} --loglevel=${{CELERYD_LOG_LEVEL}} ${{CELERYD_OPTS}}'

[Install]
WantedBy=multi-user.target"""

CELERY_TMPFILES_FILE = """d /var/run/{env.celery_service} 0755 www-data www-data -
d /var/log/{env.celery_service} 0755 www-data www-data -"""


@task
def install_celery():
    text = CELERY_SERVICE_FILE.format(env=env)
    put(StringIO(text), f'/etc/systemd/system/{env.project}_celery.service',
        use_sudo=True)
    text = CELERY_TMPFILES_FILE.format(env=env)
    put(StringIO(text), f'/etc/tmpfiles.d/{env.celery_service}.conf',
        use_sudo=True)

    sudo("systemd-tmpfiles --create")
    sudo("systemctl daemon-reload")
    sudo(f"systemctl start {env.project}_celery")


@task
def celery(cmd='status'):
    sudo(f"systemctl {cmd} {env.project}_celery", pty=False)


@task
def stop_celery():
    celery('stop')


@task
def start_celery():
    celery('start')


CERTBOT_INI = """# Use a 4096 bit RSA key instead of 2048
rsa-key-size = 4096
non-interactive
agree-tos
email = {email}

# authenticator = webroot
webroot-path = /home/certbot/webroot

domain = {host}
config-dir = /home/certbot/conf/
work-dir = /home/certbot/work/
logs-dir = /home/certbot/logs/"""


@task
def install_certbot():
    # For "Cannot add PPA. Please check that the PPA name or format is correct" error, use:
    # sudo("apt-get install -q --reinstall ca-certificates")
    # Source: https://askubuntu.com/questions/429803/cannot-add-ppa-please-check-that-the-ppa-name-or-format-is-correct

    sudo("add-apt-repository ppa:certbot/certbot")
    sudo("apt-get -qq update", pty=False)
    sudo("apt-get install -q -y certbot", pty=False)

    sudo("adduser certbot --gecos '' --disabled-password")
    conf = CERTBOT_INI.format(host=env.host, email=ADMIN_EMAIL)
    filename = '/home/certbot/certbot.ini'
    put(StringIO(conf), filename, use_sudo=True)

    put(StringIO("""#!/bin/bash\ncertbot certonly -c certbot.ini --webroot"""),
        AUTO_RENEW_SCRIPT,
        use_sudo=True, mode=0o775)
    for s in ['webroot', 'conf', 'work', 'logs']:
        sudo('mkdir -p /home/certbot/{}/'.format(s), user='certbot')
    get_cert()
    backup_cert()


@task
def get_cert():
    sudo("service nginx stop")
    with cd("/home/certbot/"):
        sudo("certbot certonly -c certbot.ini --standalone")
    sudo('chown -vR {} {}'.format("certbot", "/home/certbot/"))
    sudo("service nginx start")


@task
def backup_cert():
    get("/home/certbot/conf/", "%(host)s/certbot/%(path)s", use_sudo=True)

    # IMPORTANT NOTES:
    #  - Your account credentials have been saved in your Certbot
    #    configuration directory at /home/certbot/conf. You should make a
    #    secure backup of this folder now. This configuration directory will
    #    also contain certificates and private keys obtained by Certbot so
    #    making regular backups of this folder is ideal.


@task
def renew_cert():
    with cd("/home/certbot/"):
        sudo(AUTO_RENEW_SCRIPT, user='certbot')
    sudo("service nginx reload")


CERTBOT_CRON = """MAILTO={email}
0 0 1 FEB,APR,JUN,AUG,OCT,DEC * {}
"""


@task
def setup_certbot_crontab():
    s = CERTBOT_CRON.format(AUTO_RENEW_SCRIPT, email=ADMIN_EMAIL)
    put(StringIO(s), '/tmp/crontab')
    run('sudo -iu certbot crontab < /tmp/crontab')


@task
def nginx_log():
    sudo('tail -f /var/log/nginx/*')
    # sudo('tail -n 200 /var/log/nginx/error.log  /var/log/nginx/access.log')
