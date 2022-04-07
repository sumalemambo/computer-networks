package main

import (
	"fmt"
	"math/rand"
	"net"
)

const(
	INIT = "!INIT"
	DISCONNECT = "!DISCONNECT"
	REQUEST = "!REQUEST_MOVE"
)

func decide() int {
	if rand.Float64() <= 0.8 {
		return 1
	}
	return 0
}

func handle_client(port string, addr net.UDPAddr) {
	buf := make([]byte, 1024)
	s, _ := net.ResolveUDPAddr("udp", port)
	ln, _ := net.ListenUDP("udp", s)
	defer ln.Close()

	ln

}

func main() {

	PORT := ":5000"
	BUFFER := 1024
	s, err := net.ResolveUDPAddr("udp", PORT)
	if err != nil {
		// handle error
		return
	}

	ln, err := net.ListenUDP("udp", s)
	if err != nil {
		// handle error
		return
	}
	defer ln.Close()

	buf := make([]byte, BUFFER)

	for {
		n, addr, _ := ln.ReadFromUDP(buf)
		msg := string(buf[:n])

		switch {
			case msg == REQUEST:
				port := string(rand.Intn(65356 - 8000) + 8000)
				go handle_client(port)
				response := []byte(port)
				_, _ = ln.WriteToUDP(response, addr)
			case msg == DISCONNECT:
				break
		}
	}
	return
}