# encoding: utf-8

from fabric.api import env, local, run, cd, task, require, settings, prefix
from fabric.contrib.project import rsync_project
from fabric.colors import green, red


#
# Environments
#
@task
def vagrant():
    """
    Ambiente local de desarrollo (máquina virtual Vagrant).
    """
    # Usuario "vagrant"
    env.user = "vagrant"
    # Se conecta al ssh local
    env.hosts = ["127.0.0.1:2222"]

    # Llave ssh creada por Vagrant
    result = local("vagrant ssh-config | grep IdentityFile", capture=True)
    env.key_filename = result.split()[1]

    # Directorio del sitio Django
    env.site_dir = "/home/vagrant/app"


@task
def production():
    """
    Servidor de producción
    """
    env.user = 'rohan'
    env.hosts = ['rohan.cincoovnis.com']

    # Directorio del sitio
    env.site_dir = '/var/www/rohan.cincoovnis.com'


#
# Tasks
#
@task
def bootstrap():
    """
    A partir de un sistema "vacío", con todas las dependencias instaladas,
    prepara el ambiente para correr la aplicación en modo desarrollo.
    """
    require("site_dir")

    # Configuración de PostgreSQL
    run('sudo su -c "/home/vagrant/bootstrap/postgresql.sh" postgres')
    run('sudo ln -s /usr/lib/libproj.so.0 /usr/lib/libproj.so')

    run('createdb --template postgisdb rohan')

    syncdb()


@task
def resetdb():
    require("site_dir")

    run("dropdb rohan")
    run('createdb --template postgisdb rohan')

    syncdb()


@task
def test(test=None):
    require("site_dir")
    env.output_prefix = False
    with cd(env.site_dir):
        if test is None:
            test_command = "python manage.py test -v 0"
        else:
            test_command = "python manage.py test %s -v 0" % test
        with settings(warn_only=True):
            result = run(test_command)
        if result.failed:
            print red("Algunos tests fallaron.", bold=True)
        else:
            print green("Todos los tests pasaron con éxito.", bold=True)

    env.output_prefix = True


#
# manage.py
#
@task
def syncdb():
    require("site_dir")
    with cd(env.site_dir):
        run("python manage.py syncdb --noinput")
        run("python manage.py migrate")


@task
def runserver():
    require("site_dir")
    with cd(env.site_dir):
        run("python manage.py runserver_plus 0.0.0.0:8000")


@task
def deploy():
    """
    Deploys application to production environment.
    """
    require("site_dir")
    git_revision = local('git rev-parse HEAD', capture=True)
    git_branch = local('git rev-parse --abbrev-ref HEAD', capture=True)
    rsync_project(
        remote_dir=env.site_dir,
        local_dir='django_site/',
        exclude="*.pyc",
        delete=False
    )
    with cd(env.site_dir), prefix('source env/bin/activate'), prefix('source envvar'):
        run('pip install -r requirements/production.txt')
        run("python manage.py syncdb")
        run("python manage.py migrate")
        run("python manage.py collectstatic --noinput")
        run('touch reload')
        run('opbeat -o 1b8118e6bdb34aeb98078b4d2082f10e -a d3b642e69c -t 6014a391d67d97e1d6c40ba34e03c35c8aac0690 deployment --component path:. vcs:git rev:%s branch:%s remote_url:git@github.com:vinco/fundacion-proninos' % (git_revision, git_branch))

    print green('Deploy exitoso.')
