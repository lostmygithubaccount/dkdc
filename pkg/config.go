package pkg

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"

	"github.com/spf13/viper"
)

const defaultConfig = `# dkdc config file
[aliases]
a = "thing"
alias = "thing"
[things]
thing = "https://github.com/lostmygithubaccount/dkdc"
`

func configPath() string {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		logger.Fatal(err)
		os.Exit(1)
	}
	return filepath.Join(homeDir, ".dkdc", "config.toml")
}

func InitConfig() {
	configPath := configPath()
	configDir := filepath.Dir(configPath)

	if err := os.MkdirAll(configDir, 0o755); err != nil {
		logger.Fatal(err)
		os.Exit(1)
	}

	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		// create default config file
		if err := os.WriteFile(configPath, []byte(defaultConfig), 0o644); err != nil {
			logger.Fatal(err)
			os.Exit(1)
		}
	}

	viper.SetConfigFile(configPath)
	if err := viper.ReadInConfig(); err != nil {
		logger.Fatal(err)
		os.Exit(1)
	}
}

func ConfigIt() {
	configPath := configPath()

	editor := os.Getenv("EDITOR")
	if editor == "" {
		editor = "vi"
	}

	_, err := exec.LookPath(editor)
	if err != nil {
		logger.Fatalf("editor %s not found in PATH", editor)
		os.Exit(1)
	}

	fmt.Printf("opening %s with %s...\n", configPath, editor)

	cmd := exec.Command(editor, configPath)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		logger.Fatal(err)
		os.Exit(1)
	}
}

func GetConfig() map[string]any {
	config := viper.AllSettings()
	return config
}

func PrintConfig() {
	config := GetConfig()

	sections := []string{"aliases", "things"}

	for _, section := range sections {
		sectionData, ok := config[section]
		if !ok {
			continue
		}

		sectionMap, ok := sectionData.(map[string]any)
		if !ok {
			continue
		}

		fmt.Printf("%s:\n\n", section)

		keys := make([]string, 0, len(sectionMap))
		for k := range sectionMap {
			keys = append(keys, k)
		}
		sort.Strings(keys)

		maxKeyLen := 0
		for _, k := range keys {
			if len(k) > maxKeyLen {
				maxKeyLen = len(k)
			}
		}

		for _, k := range keys {
			fmt.Printf("• %-*s | %v\n", maxKeyLen, k, sectionMap[k])
		}

		fmt.Println()
	}
}
