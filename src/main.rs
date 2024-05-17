use clap::{Parser, Subcommand};
use dkdc;

#[derive(Parser, Debug)]
#[command(version)]
#[command(about = "don't know, don't care", long_about = None)]
#[command(arg_required_else_help = true)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,

    #[arg(help = "Message for AI chat")]
    message: Option<String>,
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
    #[command(about = "Tokenize", long_about = None)]
    #[command(arg_required_else_help = true)]
    Tokens {
        #[arg(help = "The message to tokenize")]
        string: Option<String>,

        #[arg(short, long)]
        #[arg(help = "The file to read from")]
        filepath: Option<String>,
    },
    #[command(about = "AI chat", long_about = None)]
    #[command(arg_required_else_help = true)]
    Chat {
        #[arg(help = "The message to send to the AI")]
        message: String,

        #[arg(short, long)]
        #[arg(default_value_t = 1)]
        #[arg(help = "The number of completions to generate")]
        n: u8,

        #[arg(short, long)]
        #[arg(default_value_t = 1024)]
        #[arg(help = "The maximum number of tokens to generate")]
        max_tokens: u32,

        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Verbose output")]
        verbose: bool,
    },
    #[command(about = "AI classify", long_about = None)]
    #[command(arg_required_else_help = true)]
    Classify {
        #[arg(help = "The message to classify")]
        message: Option<String>,

        #[arg(short, long)]
        #[arg(help = "The file to read from")]
        filepath: Option<String>,

        #[arg(short, long)]
        #[arg(help = "The labels to classify against")]
        labels: String,

        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Allow none of the above")]
        allow_none: bool,

        #[arg(short, long)]
        #[arg(default_value = "false")]
        #[arg(help = "Verbose output")]
        verbose: bool,

        #[arg(short, long)]
        #[arg(default_value_t = 3)]
        #[arg(help = "The number of completions to generate")]
        n: u8,
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
                AiCommands::Tokens { string, filepath } => {
                    let string = match string {
                        Some(string) => string,
                        None => {
                            let filepath = filepath.unwrap();
                            let string = dkdc::utils::filesystem::file_to_string(filepath.as_str());
                            string.unwrap()
                        }
                    };
                    dkdc::commands::ai::tokenize(string.as_str());
                }
                AiCommands::Chat {
                    message,
                    n,
                    max_tokens,
                    verbose,
                } => {
                    dkdc::commands::ai::ai_chat(message.as_str(), n, max_tokens, verbose);
                }

                AiCommands::Classify {
                    message,
                    filepath,
                    labels,
                    allow_none,
                    verbose,
                    n,
                } => {
                    let message = match message {
                        Some(message) => message,
                        None => {
                            let filepath = filepath.unwrap();
                            let message =
                                dkdc::utils::filesystem::file_to_string(filepath.as_str());
                            message.unwrap()
                        }
                    };
                    let labels =
                        dkdc::utils::strings::comma_separated_string_to_vec(labels.as_str());
                    dkdc::commands::ai::ai_classify(
                        message.as_str(),
                        labels,
                        allow_none,
                        verbose,
                        Some(n),
                    );
                }
            }
        }
        Some(Commands::Config { vim, env }) => {
            dkdc::commands::config::config_it(vim, env);
        }
        Some(Commands::Open { thing, list }) => {
            let list = thing.is_none() || list;
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
                dkdc::commands::image::resize_image(file.as_str(), output.as_str(), width, height);
            }
        },
        None => {
            if let Some(default_message) = cli.message {
                dkdc::utils::env::load_dotenv();
                dkdc::commands::ai::ai_chat(default_message.as_str(), 1, 1024, false);
            } else {
                panic!("extra impossible!");
            }
        }
        _ => {
            panic!("impossible!")
        }
    }
}

#[allow(unused)]
fn wip() {
    let text = "I found a bug";
    let labels = vec!["bug", "feature request", "inquiry"];
    let allow_none = true;
    let verbose = true;
    let n = Some(7);

    dkdc::utils::env::load_dotenv();
    let category = dkdc::ai::functions::classify(text, labels, allow_none, verbose, n);

    println!("Category: {}", category);
}

fn main() {
    //wip();
    cli();
}

// TODOs
// move library logic out of commands/*
// use just files for library code, expand to directories when it makes sense
// finish up ai/openai:
//   - finish up logit bias
//   - add cast
//   - custom functions for birdbrain
// take a look at implementing ai/claude
//
// remember the method: code, wip testing, command
// we ball
