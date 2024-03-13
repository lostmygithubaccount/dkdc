# Justfile

# load environment variables
set dotenv-load

# aliases
alias fmt:=format
alias preview:=app

# list justfile recipes
default:
    just --list

# setup
setup:
    @pip install -r dev-requirements.txt

# test
test:
    @cargo test

# build
build:
    @cargo build --release
    @cp target/release/dkdc ~/.cargo/bin

# format
format:
    @cargo fmt
#   @ruff format . || True

# install
install:
    @pip install -e '.[all]'

# uninstall
uninstall:
    @pip uninstall dkdc -y

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
    ruff format --check .

# clean
clean:
    @rm -r target || True
    
# @rm -rf dist || True
