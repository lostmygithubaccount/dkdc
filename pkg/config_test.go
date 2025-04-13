package pkg

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/spf13/viper"
)

func TestGetConfig(t *testing.T) {
	// Reset viper to ensure a clean test environment
	viper.Reset()

	// Create a temporary directory for our test config
	tmpDir := t.TempDir()
	testConfigPath := filepath.Join(tmpDir, "config.toml")

	// Create test config file
	testConfig := `[aliases]
a = "thing"
alias = "thing"
[things]
thing = "https://github.com/lostmygithubaccount/dkdc"
testitem = "https://example.com"
`
	if err := os.WriteFile(testConfigPath, []byte(testConfig), 0o644); err != nil {
		t.Fatalf("Failed to write test config: %v", err)
	}

	// Tell viper to use our test config
	viper.SetConfigFile(testConfigPath)
	if err := viper.ReadInConfig(); err != nil {
		t.Fatalf("Failed to read test config: %v", err)
	}

	// Test GetConfig
	config := GetConfig()
	if config == nil {
		t.Fatal("Expected config to not be nil")
	}

	// Check if aliases section exists
	aliases, ok := config["aliases"].(map[string]any)
	if !ok {
		t.Fatal("Expected aliases section in config")
	}

	// Check specific alias
	if a, exists := aliases["a"]; !exists || a != "thing" {
		t.Errorf("Expected alias 'a' to be 'thing', got %v", a)
	}

	// Check if things section exists
	things, ok := config["things"].(map[string]any)
	if !ok {
		t.Fatal("Expected things section in config")
	}

	// Check specific thing
	if thing, exists := things["testitem"]; !exists || thing != "https://example.com" {
		t.Errorf("Expected thing 'testitem' to be 'https://example.com', got %v", thing)
	}
}
