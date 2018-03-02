from io import StringIO

from fabric.api import *

# env.user = "sysop"
env.user = "mosaic"
env.hosts = ["178.79.161.158"]


@task
def host_type():
    run("uname -a")


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
    sudo(f"DEBIAN_FRONTEND=noninteractive apt-get install -y -q {pkgs}", pty=False)


@task
def uptime():
    run("uptime")


@task
def apt_upgrade():
    sudo("apt-get update", pty=False)
    sudo("apt-get upgrade -y", pty=False)


@task
def create_postgres_su():
    run(f"sudo -u postgres createuser -s {env.user}")
    run(f"createdb {env.user}")


env.project = "mosaic_prj"
env.code_dir = f"/home/sysop/{env.project}"
env.clone_url = "git@github.com:yaniv14/mosaic_prj.git"


@task
def clone_project():
    run(f"git clone {env.clone_url} {env.code_dir}", pty=False)


env.venv_name = "mosaic"
env.venvs = f"/home/sysop/.virtualenvs/"
env.venv_path = f"{env.venvs}{env.venv_name}/"
env.venv_command = f"source {env.venv_path}/bin/activate"


@task
def create_venv():
    run(f"mkdir -p {env.venvs}")
    run(f"virtualenv -p /usr/bin/python3 --prompt='({env.venv_name}) ' {env.venv_path}")


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
        run("git pull", pty=False)


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

env.app_name = "mosaic_prj"
env.wsgi_file = "mosaic_prj/wsgi.py"
env.stats_port = 9000


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
server {{
    listen      80;
    server_name {host};
    charset     utf-8;

    location /static/ {{
        alias {env.static_path};
    }}

    location / {{
        uwsgi_pass  unix://{env.uwsgi_socket};
        include     uwsgi_params;
    }}
}}"""

env.uwsgi_socket = f"/run/uwsgi/app/{env.app_name}/socket"
env.static_path = f"{env.code_dir}/collected_static/"


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
def uwsgi_log():
    sudo("tail /var/log/uwsgi/app/ifx.log")


@task
def git_pull():
    with virtualenv():
        run("git pull", pty=False)


@task
def collect_static():
    m('collectstatic --noinput')


@task
def reload_app():
    sudo('systemctl reload uwsgi.service')


@task
def upgrade():
    git_pull()
    migrate()
    collect_static()
    reload_app()
