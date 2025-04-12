# justfile

# load environment variables
set dotenv-load

# aliases
alias fmt:=format
alias tidy:=sync
alias install:=setup

# list justfile recipes
default:
    just --list

# setup
setup:
    go install .

# sync
sync:
    go mod tidy

# build
build:
    mkdir -p bin
    go build -o ./bin .

# test
test *args:
    go test ./... {{ args }}

# run
run *args:
    go run . {{ args }}

# format
format:
    gofmt -w -s .

# publish-test
release-test:
    echo "TODO"

# publish
release:
    echo "TODO"

# open
open:
    open https://github.com/lostmygithubaccount/dkdc
