package pkg

import (
	"fmt"
	"os"
	"os/exec"

	"github.com/spf13/viper"
)

func aliasOrThingToUri(thing string) (string, error) {
	config := viper.AllSettings()

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

func OpenThings(things []string) {
	for _, thing := range things {
		thing, err := aliasOrThingToUri(thing)
		if err != nil {
			logger.Fatalf("failed to resolve %s: %v", thing, err)
			os.Exit(1)
		}
		openIt(thing)
	}
}
