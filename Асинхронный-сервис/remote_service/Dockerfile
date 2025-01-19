FROM golang:1.21.0-alpine AS builder

COPY . /build/
WORKDIR /build/

RUN go mod download
RUN go clean --modcache
RUN go build -mod=readonly -o ./.bin ./cmd/main.go

ENV TZ="Europe/Moscow"
ENV ZONEINFO=/zoneinfo.zip

ENTRYPOINT ["./.bin"]