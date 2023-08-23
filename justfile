# Justfile

# load environment variables
set dotenv-load

# aliases
alias preview:=app

# list justfile recipes
default:
    just --list

# setup
setup:
    @pip install -r dev-requirements.txt

# build
build:
    just clean
    @python -m build

# install
install:
    @pip install -e '.[all]'

# publish-test
release-test:
    just build
    @twine upload --repository testpypi dist/* -u __token__ -p ${PYPI_TEST_KEY}

# publish
release:
    just build
    @twine upload dist/* -u __token__ -p ${PYPI_KEY}

# streamlit stuff
app:
    @streamlit run app.py

# smoke-test
smoke-test:
    black --check .

# clean
clean:
    @rm -rf dist || True
    @pip uninstall dkdc -y


