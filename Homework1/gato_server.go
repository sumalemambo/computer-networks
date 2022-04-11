package main

import (
	"fmt"
	"math/rand"
	"net"
	"strconv"
	"strings"
)

// Define message types between server and gato_server
const(
	PORT = ":5000"
	BUFFER = 1024
	INIT = "!INIT"
	REQUEST = "!REQUEST_MOVE"
	AVAILABLE = "!AVAILABLE"
	NOT_AVAILABLE = "!NOT_AVAILABLE"
)


// Function to listen UDP messages on random ports and send random plays back
func handle_client(port string) {
	buf := make([]byte, BUFFER)
	s, _ := net.ResolveUDPAddr("udp", port)
	ln, _ := net.ListenUDP("udp", s)

	defer ln.Close()

	n, addr, _ := ln.ReadFromUDP(buf)

	fmt.Printf("[NEW CONNECTION] %s connected\n", addr)
	msg := string(buf[:n])
	fmt.Printf("[CLIENT MESSAGE] %s sent by %s\n", msg, addr)
	// msg contains the empty cells in the table
	empty_cells := strings.Split(msg, ", ")
	// Select one of the n possible empty cells and return the play
	response := []byte(empty_cells[rand.Intn(len(empty_cells))])
	// Send the move back to the server
	_, _ = ln.WriteToUDP(response, addr)
}

func main() {
	// Transform local address into UDP address
	s, err := net.ResolveUDPAddr("udp", PORT)
	if err != nil {
		// handle error
		return
	}

	// Init UDP listening on UDP address
	ln, err := net.ListenUDP("udp", s)
	if err != nil {
		// handle error
		return
	}
	// Once the main function stops the server will close
	defer ln.Close()

	buf := make([]byte, BUFFER)

	fmt.Printf("[LISTENING] Listening on %s\n", s)
	for {
		n, addr, _ := ln.ReadFromUDP(buf)
		msg := string(buf[:n])
		fmt.Printf("[NEW CONNECTION] %s connected\n", addr)
		fmt.Printf("[CLIENT MESSAGE] %s sent by %s\n", msg, addr)
		
		// Handle the different messsages
		switch {
			case msg == INIT:
				if rand.Float64() <= 0.8 {
					response := []byte(AVAILABLE)
					_, _ = ln.WriteToUDP(response, addr)
				} else {
					response := []byte(NOT_AVAILABLE)
					_, _ = ln.WriteToUDP(response, addr)
				}
			case msg == REQUEST:
				// rand.Intn(65535 - 8000) = rand.Intn(57535)
				port := strconv.Itoa(rand.Intn(57535) + 8000)
				go handle_client(":" + port)
				response := []byte(port)
				_, _ = ln.WriteToUDP(response, addr)
			default:
				return
		}
	}
}