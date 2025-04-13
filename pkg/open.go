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
	openCmd := "open"
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

func OpenThings(things []string, fast bool) {
	if fast {
		maxWorkers := runtime.NumCPU()

		jobs := make(chan string, len(things))

		var wg sync.WaitGroup

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

		for _, thing := range things {
			jobs <- thing
		}

		close(jobs)

		wg.Wait()
	} else {
		for _, thing := range things {
			uri, err := aliasOrThingToUri(thing)
			if err != nil {
				logger.Printf("skipping %s: %v", thing, err)
				continue
			}
			openIt(uri)
		}
	}
}
