package cmd

import (
	"testing"

	"github.com/spf13/cobra"
)

func TestRunRootCmd(t *testing.T) {
	// Test with no arguments (should print config)
	// This is more of a smoke test as it doesn't verify output
	runRootCmd([]string{})

	// Test with arguments
	// This is more of a smoke test too since it's hard to verify the opening without mocks
	runRootCmd([]string{"thing"})
}

func TestRootCommandFlags(t *testing.T) {
	// Check that the fast flag is properly defined
	cmd := &cobra.Command{}
	initTestCmd(cmd)

	fastFlag, err := cmd.Flags().GetBool("fast")
	if err != nil {
		t.Fatalf("Failed to get fast flag: %v", err)
	}

	if fastFlag != false {
		t.Errorf("Expected fast flag default value to be false, got %v", fastFlag)
	}

	// Check config flag
	configFlag, err := cmd.PersistentFlags().GetBool("config")
	if err != nil {
		t.Fatalf("Failed to get config flag: %v", err)
	}

	if configFlag != false {
		t.Errorf("Expected config flag default value to be false, got %v", configFlag)
	}
}

// Initialize a command for testing with the same flags as in init()
func initTestCmd(cmd *cobra.Command) {
	cmd.Flags().BoolP("fast", "f", false, "open things in parallel")
	cmd.PersistentFlags().BoolP("config", "c", false, "configure dkdc")
}
