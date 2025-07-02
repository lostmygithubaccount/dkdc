use anyhow::Result;

fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    dkdc_cli::run_cli(args)
}
