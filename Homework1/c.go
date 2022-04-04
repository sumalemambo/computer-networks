package main

import (
	"fmt"
	"net"
)

func md() {

	PORT := ":5000"
	BUFFER := 1024
	s, err := net.ResolveUDPAddr("udp4", PORT)

	if err != nil {
		fmt.Println(err)
		return
	}

	connection, err := net.ListenUDP("udp4", s)
	if err != nil {
		fmt.Println(err)
		return
	}

	defer connection.Close()

	buffer := make([]byte, BUFFER)

	fmt.Println("esperando mensaje del servidor intermedio")
	n, addr, _ := connection.ReadFromUDP(buffer)
	msg := string(buffer[:n])

	fmt.Println("direccion:", addr)
	fmt.Println("mensaje del servidor intermedio:", msg)
	response := []byte("adios")
	_, _ = connection.WriteToUDP(response, addr)
	return
}
