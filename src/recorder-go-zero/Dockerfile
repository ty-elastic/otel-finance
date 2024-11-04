FROM golang:1.23.1-alpine AS builder
WORKDIR /usr/src/app/

COPY go.* ./
COPY *.go ./
RUN go build -o /go/bin/recorder-zero

# -----------------------------------------------------------------------------

FROM alpine

COPY --from=builder /go/bin/recorder-zero /recorder-zero

EXPOSE 9003
ENTRYPOINT [ "/recorder-zero" ]
