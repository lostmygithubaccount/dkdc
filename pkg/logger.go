package pkg

import (
	"log"
)

var logger = log.New(log.Writer(), "[dkdc] ", log.LstdFlags|log.Lshortfile)
