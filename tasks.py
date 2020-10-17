import os
import sys
from shutil import rmtree

from invoke import Exit, task

try:
    input = raw_input
except NameError:
    pass


BASE_FOLDER = os.path.dirname(__file__)


class Log(object):
    def __init__(self, out=sys.stdout, err=sys.stderr):
        self.out = out
        self.err = err

    def flush(self):
        self.out.flush()
        self.err.flush()

    def write(self, message):
        self.flush()
        self.out.write(message + '\n')
        self.out.flush()

    def info(self, message):
        self.write('[INFO] %s' % message)

    def warn(self, message):
        self.write('[WARN] %s' % message)


log = Log()


def confirm(question):
    while True:
        response = input(question).lower().strip()
        if not response or response in ('n', 'no'):
            return False
        if response in ('y', 'yes'):
            return True
        print('Focus, kid! It is either (y)es or (n)o', file=sys.stderr)


@task(default=True)
def help(ctx):
    """Lists available tasks and usage."""
    ctx.run('invoke --list')
    log.write('Use "invoke -h <taskname>" to get detailed help for a task.')


@task(help={
    'docs': 'True to clean up generated documentation, otherwise False',
    'bytecode': 'True to clean up compiled python files, otherwise False.',
    'builds': 'True to clean up build/packaging artifacts, otherwise False.'
})
def clean(ctx, docs=True, bytecode=True, builds=True):
    """Cleans the local copy from compiled artifacts."""
    if builds:
        ctx.run('python setup.py clean')
    if bytecode:
        for root, dirs, files in os.walk(BASE_FOLDER):
            for f in files:
                if f.endswith('.pyc'):
                    os.remove(os.path.join(root, f))
            if '.git' in dirs:
                dirs.remove('.git')
    folders = []
    folders.append('dist/')
    if docs:
        folders.append('docs/api/generated')
    if bytecode:
        folders.append('src/compas_cgal/__pycache__')
    if builds:
        folders.append('build/')
        folders.append('src/compas_cgal.egg-info/')
    for folder in folders:
        rmtree(os.path.join(BASE_FOLDER, folder), ignore_errors=True)


@task(help={
    'rebuild': 'True to clean all previously built docs before starting, otherwise False.',
    'doctest': 'True to run doctests, otherwise False.',
    'check_links': 'True to check all web links in docs for validity, otherwise False.'})
def docs(ctx, doctest=False, rebuild=True, check_links=False):
    """Builds package's HTML documentation."""
    if rebuild:
        clean(ctx)
    if doctest:
        ctx.run('sphinx-build -b doctest docs dist/docs')
    ctx.run('sphinx-build -E docs dist/docs')
    if check_links:
        ctx.run('sphinx-build -b linkcheck docs dist/docs')


@task()
def check(ctx):
    """Check the consistency of documentation, coding style and a few other things."""
    log.write('Checking MANIFEST.in...')
    ctx.run('check-manifest')
    log.write('Checking metadata...')
    ctx.run('python setup.py check --strict --metadata')


@task()
def lint(ctx):
    """Check the consistency of coding style."""
    log.write('Running flake8 python linter...')
    ctx.run('flake8 src')


@task(help={
    'checks': 'True to run all checks before testing, otherwise False.'})
def test(ctx, checks=False, doctest=False):
    """Run all tests."""
    if checks:
        check(ctx)
    cmd = ['pytest']
    if doctest:
        cmd.append('--doctest-modules')
    ctx.run(' '.join(cmd))


@task(help={
    'version_type': 'Type of version follows semver rules. Must be one of: major, minor, patch.'})
def bumpversion(ctx, version_type):
    """Bump the version"""
    if version_type not in ('patch', 'minor', 'major'):
        raise Exit('The version type parameter is invalid.\nMust be one of: major, minor, patch')
    # Bump version and git tag it
    ctx.run('bumpversion %s --verbose' % version_type)
