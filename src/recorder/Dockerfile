FROM golang:1.23.1-alpine AS builder
WORKDIR /usr/src/app/

COPY . ./
RUN go build -o /go/bin/recorder

# -----------------------------------------------------------------------------

FROM alpine

WORKDIR /usr/src/app/

COPY --from=builder /go/bin/recorder ./

EXPOSE 9000
ENTRYPOINT [ "./recorder" ]
