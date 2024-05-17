# Justfile

# load environment variables
set dotenv-load

# aliases
alias fmt:=format

# list justfile recipes
default:
    just --list

# setup
setup:
    @uv pip install -r dev-requirements.txt

# build
build:
    just clean
    @python -m build

# format
format:
    @ruff format . || True

# install
install:
    @uv pip install -e '.[all]' --reinstall-package dkdc

# uninstall
uninstall:
    @uv pip uninstall dkdc -y

# publish-test
release-test:
    just build
    @twine upload --repository testpypi dist/* -u __token__ -p ${PYPI_TEST_TOKEN}

# publish
release:
    just build
    @twine upload dist/* -u __token__ -p ${PYPI_TOKEN}

# smoke-test
smoke-test:
    ruff format --check .

# clean
clean:
    @rm -r dist || True
    
