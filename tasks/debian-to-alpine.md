# move from debian to alpine

I want to move from a debian-based to alpine-based image -- specifically ghcr.io/astral-sh/uv:alpine.

Move my Dockerfile from debian to alpine, testing it builds & `docker compose up` works for my stack here. Prefer using apk to install things (e.g. `github-cli` instead of the current curl stuff; probably zola directly; add btop in).

