package main

import (
	"net/http"

	"github.com/gorilla/mux"
)

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/", HomeHandler)
	http.ListenAndServe(":8080", r)
}

func HomeHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Hello, World!"))
}
