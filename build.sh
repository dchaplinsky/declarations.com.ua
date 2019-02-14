#!/bin/sh

set -xe

NAME=declarations.com.ua
VERSION=$(git rev-parse HEAD)
TAG=$(git describe --tags 2>/dev/null || echo "latest")

docker build -t ${NAME}:${TAG} -t hub:5000/${NAME}:${TAG} --build-arg version=${VERSION} .
