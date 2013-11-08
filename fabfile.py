# encoding: utf-8
import os

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
    env.user = 'root'
    env.hosts = ['doko']

    # Directorio del sitio
    env.site_dir = '/var/www/vhosts/doko/app'


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

    run('createdb --template postgisdb doko')

    syncdb()
    collectstatic()


@task
def resetdb():
    require("site_dir")

    run("dropdb doko")
    run('createdb --template postgisdb doko')

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
            print red("""
                 ,--.!,
               __/   -*-
             ,d08b.  '|`
             0088MM
             `9MMP'
            """)
        else:
            print green("Todos los tests pasaron con éxito.", bold=True)
            print green(r"""
            ,___,
            [O.o]
            /)__)
            -"--"-
            """)

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
def schemamigration(app):
    require("site_dir")
    with cd(env.site_dir):
        with settings(warn_only=True):
            run("python manage.py schemamigration --auto %s" % app)


@task
def collectstatic():
    require("site_dir")
    with cd(env.site_dir):
        run("python manage.py collectstatic --noinput")


@task
def runserver():
    require("site_dir")
    with cd(env.site_dir):
        run("python manage.py runserver_plus 0.0.0.0:8000")


@task
def deploy():
    require("site_dir")
    rsync_project(
        remote_dir=os.path.join(env.site_dir, '..'),
        local_dir='./app',
        delete=False
    )
    with cd(env.site_dir):
        pidfile = os.path.join(env.site_dir, 'doko.pid')
        run("if [ -f {0} ]; then kill -TERM `cat {0}` && rm {0}; fi".format(pidfile))
        with prefix("source env/bin/activate"):
            run("python manage.py syncdb")
            run("python manage.py migrate")
            run("python manage.py collectstatic")
            run("gunicorn_django --bind 0.0.0.0:8000 --workers 4 --daemon --pid %s" % pidfile)
    print green('Deploy exitoso.')
