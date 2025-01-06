FROM golang:1.23.1-alpine AS builder
WORKDIR /usr/src/app/

COPY go.* ./
COPY *.go ./
COPY lib lib
RUN go build -o /go/bin/recorder

# -----------------------------------------------------------------------------

FROM alpine

WORKDIR /usr/src/app/

COPY --from=builder /go/bin/recorder ./

ENV OTEL_SERVICE_NAME="recorder-go"

EXPOSE 9003
ENTRYPOINT [ "./recorder" ]
