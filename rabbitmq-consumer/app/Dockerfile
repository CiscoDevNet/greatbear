FROM golang:1.18-alpine as build

RUN apk add --no-cache git

WORKDIR /src 
COPY consumer.go /src 

RUN GO111MODULE="off" go get \
  github.com/sirupsen/logrus \
  github.com/streadway/amqp \
  github.com/cenkalti/backoff

RUN GO111MODULE="off" go build consumer.go


FROM alpine as runtime

COPY --from=build /src/consumer /app/consumer

CMD [ "/app/consumer" ]
