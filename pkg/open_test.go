package pkg

import (
	"strings"
	"testing"

	"github.com/spf13/viper"
)

func setupTestConfig() {
	// Setup config for testing
	viper.Reset()
	viper.SetConfigType("toml")

	testConfig := `
[aliases]
a = "thing"
alias = "thing"
multi = "complex-thing"
[things]
thing = "https://github.com/lostmygithubaccount/dkdc"
complex-thing = "https://example.com/complex"
`
	viper.ReadConfig(strings.NewReader(testConfig))
}

func TestAliasOrThingToUri(t *testing.T) {
	setupTestConfig()

	tests := []struct {
		name        string
		input       string
		expectedURI string
		expectError bool
	}{
		{
			name:        "Direct thing lookup",
			input:       "thing",
			expectedURI: "https://github.com/lostmygithubaccount/dkdc",
			expectError: false,
		},
		{
			name:        "Alias lookup",
			input:       "a",
			expectedURI: "https://github.com/lostmygithubaccount/dkdc",
			expectError: false,
		},
		{
			name:        "Another alias lookup",
			input:       "alias",
			expectedURI: "https://github.com/lostmygithubaccount/dkdc",
			expectError: false,
		},
		{
			name:        "Multi-level aliasing",
			input:       "multi",
			expectedURI: "https://example.com/complex",
			expectError: false,
		},
		{
			name:        "Non-existent thing",
			input:       "nonexistent",
			expectedURI: "",
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			uri, err := aliasOrThingToUri(tt.input)

			if tt.expectError {
				if err == nil {
					t.Errorf("Expected error for input '%s', but got none", tt.input)
				}
			} else {
				if err != nil {
					t.Errorf("Didn't expect error for input '%s', but got: %v", tt.input, err)
				}
				if uri != tt.expectedURI {
					t.Errorf("For input '%s', expected URI '%s', but got '%s'", tt.input, tt.expectedURI, uri)
				}
			}
		})
	}
}
