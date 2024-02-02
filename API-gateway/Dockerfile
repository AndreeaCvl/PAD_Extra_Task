# Using the Golang image
FROM golang:1.21-alpine

WORKDIR /go/src/app

COPY . .

# RUN go get -u github.com/gorilla/mux
RUN go get -u github.com/go-redis/redis/v8
RUN go get -u github.com/afex/hystrix-go/hystrix

RUN go build -o gateway

EXPOSE 8080

CMD ["./gateway"]