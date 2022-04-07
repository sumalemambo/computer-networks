package main

import (
	"fmt"
	"math/rand"
	"net"
	"strconv"
)

const(
	PORT = ":5000"
	BUFFER = 1024
	REQUEST = "!REQUEST_MOVE"
	DISCONNECT = "!DISCONNECT"
	NOT_AVAILABLE = "!NOT_AVAILABLE"
)

func handle_client(port string) {
	buf := make([]byte, BUFFER)
	s, _ := net.ResolveUDPAddr("udp", port)
	ln, _ := net.ListenUDP("udp", s)
	defer ln.Close()

	n, addr, _ := ln.ReadFromUDP(buf)
	msg := []byte(string(buf[:n]))
	_, _ = ln.WriteToUDP(msg, addr)
	return
}

func main() {
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

	fmt.Print("[LISTENING]")
	for {
		n, addr, _ := ln.ReadFromUDP(buf)
		fmt.Println("[NEW CONNECTION] ", addr)
		msg := string(buf[:n])

		switch {
			case msg == REQUEST:
				if rand.Float64() <= 0.8 {
					port := ":" + strconv.Itoa(rand.Intn(65356 - 8000) + 8000)
					go handle_client(port)
					response := []byte(port)
					_, _ = ln.WriteToUDP(response, addr)
				} else {
					response := []byte(NOT_AVAILABLE)
					_, _ = ln.WriteToUDP(response, addr)
				}
			case msg == DISCONNECT:
				break
		}
	}
	return
}