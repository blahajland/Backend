package main

import (
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/", HomeHandler)                         // POST
	r.HandleFunc("/api/sites/create", SiteCreationHandler) // POST
	r.HandleFunc("/api/sites/delete", SiteDeletionHandler) // POST
	r.HandleFunc("/api/sites/update", SiteListHandler)     // POST
	r.HandleFunc("/api/sites/list", SiteCreationHandler)   // POST
	r.HandleFunc("/api/sites/login", SiteLoginHandler)     // POST
	r.Use(Middleware)

	http.ListenAndServe(":8080", r)
}

func Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Println(r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}

func SiteCreationHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Hello, World!"))
}
func SiteDeletionHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Hello, World!"))
}
func SiteUpdateHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Hello, World!"))
}
func SiteListHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Hello, World!"))
}
func SiteLoginHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Hello, World!"))
}
func HomeHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Hello, World!"))
}
