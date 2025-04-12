package cmd

import (
	"fmt"
	"os"

	"github.com/lostmygithubaccount/dkdc/pkg"
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "dkdc",
	Short: "bookmarks in your terminal",
	Run: func(cmd *cobra.Command, args []string) {
		runRootCmd(args)
	},
}

func runRootCmd(things []string) {
	if len(things) == 0 {
		pkg.PrintConfig()
	} else {
		pkg.OpenThings(things)
	}
}

func init() {
	cobra.OnInitialize(pkg.InitConfig)

	rootCmd.PersistentFlags().BoolP("config", "c", false, "configure dkdc")

	rootCmd.PersistentPreRun = func(cmd *cobra.Command, args []string) {
		configFlag, _ := cmd.Flags().GetBool("config")
		if configFlag {
			pkg.ConfigIt()
			os.Exit(0)
		}
	}
}

func Execute() {
	rootCmd.CompletionOptions.HiddenDefaultCmd = true
	rootCmd.SetHelpCommand(&cobra.Command{Hidden: true})

	err := rootCmd.Execute()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
