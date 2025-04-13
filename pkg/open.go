package pkg

import (
	"fmt"
	"os"
	"os/exec"
	"runtime"
	"sync"
)

func aliasOrThingToUri(thing string) (string, error) {
	config := GetConfig()

	if aliases, ok := config["aliases"].(map[string]any); ok {
		if alias, exists := aliases[thing]; exists {
			thing = alias.(string)
		}
	}

	if things, ok := config["things"].(map[string]any); ok {
		if uri, exists := things[thing]; exists {
			return uri.(string), nil
		}
	}

	return "", fmt.Errorf("'%s' not found in [things] or [aliases]", thing)
}

func openIt(thing string) {
	var openCmd string
	switch runtime.GOOS {
	case "darwin":
		openCmd = "open"
	case "linux":
		openCmd = "xdg-open"
	default:
		logger.Fatalf("unsupported OS: %s", runtime.GOOS)
	}

	_, err := exec.LookPath(openCmd)
	if err != nil {
		logger.Fatalf("command %s not found in PATH", openCmd)
		os.Exit(1)
	}

	cmd := exec.Command(openCmd, thing)
	if err := cmd.Run(); err != nil {
		logger.Fatalf("failed to open %s: %v", thing, err)
	}
	fmt.Printf("opening %s...\n", thing)
}

func OpenThings(things []string, maxWorkers int) {
	var wg sync.WaitGroup
	jobs := make(chan string, len(things))
	numCPU := runtime.NumCPU()

	for _, thing := range things {
		jobs <- thing
	}
	close(jobs)

	if maxWorkers <= 0 || maxWorkers > numCPU {
		maxWorkers = numCPU
	}

	for range maxWorkers {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for thing := range jobs {
				uri, err := aliasOrThingToUri(thing)
				if err != nil {
					logger.Printf("skipping %s: %v", thing, err)
					continue
				}
				openIt(uri)
			}
		}()
	}

	wg.Wait()
}
