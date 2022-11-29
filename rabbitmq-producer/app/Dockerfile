FROM golang:1.18-alpine as build

RUN apk add --no-cache git

WORKDIR /src 
COPY producer.go /src 

RUN GO111MODULE="off" go get \
  github.com/julienschmidt/httprouter \
  github.com/sirupsen/logrus \
  github.com/streadway/amqp

RUN GO111MODULE="off" go build producer.go


FROM alpine as runtime

COPY --from=build /src/producer /app/producer

CMD [ "/app/producer" ]
