package main

import (
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/julienschmidt/httprouter"
	log "github.com/sirupsen/logrus"
	"github.com/streadway/amqp"
)

var rabbit_host = os.Getenv("RABBIT_HOST")
var rabbit_port = os.Getenv("RABBIT_PORT")
var rabbit_username = os.Getenv("RABBIT_USERNAME")
var rabbit_password = os.Getenv("RABBIT_PASSWORD")
var rabbit_queue = os.Getenv("RABBIT_QUEUE")

var seqNum int

func main() {
	err := validateEnv()
	if err != nil {
		log.Fatalf("%s", err)
	}

	go func() {
		for {
			seqNum += 1
			err := produce(fmt.Sprintf("auto produced message #%d", seqNum))
			if err != nil {
				log.Printf("stopping loop. error producing message %d: %s\n", seqNum,
					err)
				return
			}
			time.Sleep(5 * time.Second)
		}
	}()

	router := httprouter.New()
	router.POST("/produce/:message", submit)

	log.Println("Running...")
	log.Fatal(http.ListenAndServe(":80", router))
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

func submit(writer http.ResponseWriter, request *http.Request, p httprouter.Params) {
	message := p.ByName("message")

	log.Println("Received message: " + message)
	err := produce(message)
	if err != nil {
		log.Fatalf("%s", err)
		return
	}

	log.Println("produce success!")
}

func produce(message string) error {
	conn, err := amqp.Dial(fmt.Sprintf("amqp://%s:%s@%s:%s/",
		rabbit_username,
		rabbit_password,
		rabbit_host,
		rabbit_port))
	if err != nil {
		return fmt.Errorf("Failed to connect to RabbitMQ: %s", err)
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

	err = ch.Publish(
		"",     // exchange
		q.Name, // routing key
		false,  // mandatory
		false,  // immediate
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(message),
		})
	if err != nil {
		return fmt.Errorf("Failed to produce a message: %s", err)
	}

	log.Printf("Produced a message: <%s>", message)
	return nil
}
