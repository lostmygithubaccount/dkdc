use clap::{Parser, Subcommand};
use dkdc;

#[derive(Parser, Debug)]
#[command(version)]
#[command(about = "don't know, don't care", long_about = None)]
#[command(arg_required_else_help = true)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand, Debug)]
enum Commands {
    #[command(about = "AI commands", long_about = None)]
    #[command(arg_required_else_help = true)]
    Ai {
        #[command(subcommand)]
        subcommand: AiCommands,
    },

    #[command(about = "Configure things (config.toml by default)", long_about = None)]
    #[command(aliases = &["c"])]
    Config {
        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Open the .env file")]
        env: bool,

        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Open with nvim")]
        vim: bool,
    },

    #[command(about = "Open things", long_about = None)]
    #[command(aliases = &["o"])]
    #[command(arg_required_else_help = false)]
    Open {
        thing: Option<String>,

        #[arg(short, long)]
        #[arg(help = "List the things and aliases")]
        list: bool,
    },

    #[command(about = "Print numbers", long_about = None)]
    Run {
        #[arg(short, long)]
        #[arg(default_value_t = 1_000_000_000)]
        max: u128,

        #[arg(short, long)]
        #[arg(default_value_t = 1_000_000)]
        divisor: u128,
    },

    #[command(about = "Image commands", long_about = None)]
    #[command(arg_required_else_help = true)]
    Image {
        #[command(subcommand)]
        subcommand: ImageCommands,
    },
}

#[derive(Subcommand, Debug)]
enum AiCommands {
    #[command(about = "AI default", long_about = None)]
    Default {
        #[arg(default_value = "https://dkdc.dev")]
        url: Option<String>,
    },
    #[command(about = "AI testing", long_about = None)]
    Testing {
        //#[arg(short, long)]
        #[arg(default_value = "What is 2+2?")]
        message: String,
    },
}

#[derive(Subcommand, Debug)]
enum ImageCommands {
    #[command(about = "Resize an image", long_about = None)]
    Resize {
        #[arg(short, long)]
        #[arg(default_value = "thumbnail.png")]
        file: String,

        #[arg(short, long)]
        #[arg(default_value = "resized.png")]
        output: String,

        #[arg(short = 'W', long)]
        #[arg(default_value_t = 512)]
        width: u32,

        #[arg(short = 'H', long)]
        #[arg(default_value_t = 512)]
        height: u32,
    },
}

#[allow(unused)]
fn cli() {
    let cli = Cli::parse();

    match cli.command {
        Some(Commands::Ai { subcommand }) => {
            dkdc::utils::env::load_dotenv();
            match subcommand {
                AiCommands::Testing { message } => {
                    dkdc::commands::ai::ai_testing(message.as_str());
                }
                AiCommands::Default { url } => {
                    dkdc::commands::ai::ai(url.as_deref().unwrap());
                }
            }
        }
        Some(Commands::Config { vim, env }) => {
            dkdc::commands::open::config_it(vim, env);
        }
        Some(Commands::Open { thing, list }) => {
            dkdc::commands::open::open_it(thing, list);
        }
        Some(Commands::Run { max, divisor }) => {
            dkdc::commands::testing::print_numbers(max, divisor);
        }
        Some(Commands::Image { subcommand }) => match subcommand {
            ImageCommands::Resize {
                file,
                output,
                width,
                height,
            } => {
                dkdc::commands::image::resize_image(file.as_str(), output.as_str(), width, height)
                    .expect("whoops");
            }
        },
        _ => {
            panic!("impossible!")
        }
    }
}

#[allow(unused)]
fn wip() {
    dkdc::ai::openai::chat_completions("What is 2+2?");
}

fn main() {
    cli();
}
