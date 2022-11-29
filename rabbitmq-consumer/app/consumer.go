package main

import (
	"fmt"
	"os"
	"time"

	"github.com/cenkalti/backoff"
	log "github.com/sirupsen/logrus"
	"github.com/streadway/amqp"
)

var rabbit_host = os.Getenv("RABBIT_HOST")
var rabbit_port = os.Getenv("RABBIT_PORT")
var rabbit_username = os.Getenv("RABBIT_USERNAME")
var rabbit_password = os.Getenv("RABBIT_PASSWORD")
var rabbit_queue = os.Getenv("RABBIT_QUEUE")

func main() {
	err := validateEnv()
	if err != nil {
		log.Fatalf("%s", err)
	}

	err = consume()
	if err != nil {
		log.Fatalf("%s", err)
	}
}

func validateEnv() error {
	if rabbit_host == "" {
		return fmt.Errorf("missing RABBIT_HOST env")
	}
	if rabbit_port == "" {
		return fmt.Errorf("missing RABBIT_PORT env")
	}
	if rabbit_username == "" {
		return fmt.Errorf("missing RABBIT_USERNAME env")
	}
	if rabbit_password == "" {
		return fmt.Errorf("missing RABBIT_PASSWORD env")
	}
	if rabbit_queue == "" {
		return fmt.Errorf("missing RABBIT_QUEUE env")
	}

	return nil
}

func consume() error {

	b := backoff.NewExponentialBackOff()
	b.InitialInterval = 2 * time.Second
	b.MaxInterval = 10 * time.Minute
	b.MaxElapsedTime = 1 * time.Hour
	conn, err := amqp.Dial(fmt.Sprintf("amqp://%s:%s@%s:%s/",
		rabbit_username,
		rabbit_password,
		rabbit_host,
		rabbit_port))
	if err != nil {
		backoffError := backoff.Retry(func() error {
			conn, err = amqp.Dial(fmt.Sprintf("amqp://%s:%s@%s:%s/",
				rabbit_username,
				rabbit_password,
				rabbit_host,
				rabbit_port))
			return err
		}, b)
		if backoffError != nil {
			return fmt.Errorf("Failed to connect to RabbitMQ: %s", err)
		}
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		return fmt.Errorf("Failed to open a channel: %s", err)
	}
	defer ch.Close()

	q, err := ch.QueueDeclare(
		rabbit_queue, // name
		true,         // durable
		false,        // delete when unused
		false,        // exclusive
		false,        // no-wait
		nil,          // arguments
	)
	if err != nil {
		return fmt.Errorf("Failed to declare a queue: %s", err)
	}

	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer
		false,  // auto-ack
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // args
	)
	if err != nil {
		return fmt.Errorf("Failed to register consumer: %s", err)
	}

	forever := make(chan bool)

	go func() {
		for d := range msgs {
			log.Printf("Received a message: <%s>", d.Body)
			d.Ack(false)
		}
	}()

	log.Println("Running...")
	<-forever
	return nil
}
