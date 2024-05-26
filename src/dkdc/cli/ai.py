# imports
import typer

from dkdc.utils import filesystem as fs
from dkdc.ai.models import File
from dkdc.ai.openai import Client
from dkdc.cli.console import print


# functions
def run_ai() -> None:
    """
    chat with ai
    """
    client = Client()
    print("starting dkdc.ai...")

    while True:
        response = None
        text = typer.prompt("user").strip()
        print(text, header="user")
        start = text.split()[0]
        match start:
            case "exit" | "e" | "quit" | "q":
                print("exiting dkdc.ai...")
                break
            case "load" | "l":
                try:
                    pattern = text.split()[1]
                except IndexError:
                    print("no pattern provided")
                    pattern = "src/**"

                files = fs.list_files(pattern)
                files_dict = fs.read_files(files)

                client.add_context(files_dict)

                response = f"loading pattern: {pattern}..."
                files_bullets = "\n\n- " + "\n\n- ".join(files)
                response += f"\n\nfiles: {files_bullets}"
            case "write" | "w":
                # TODO: not working well in general
                additional_instructions = "Follow the user's instruction and extract the relevant filename and content."
                additional_instructions += "\n\nALWAYS default to temp.<ext> if no explicit filename is provided to write to."
                additional_instructions += "\n\nExtract ONLY the file contents, nothing additional (e.g. only Python code)."

                text = "" + client.messages[-1].json() + client.messages[-2].json()

                file = client.cast(
                    text, File, additional_instructions=additional_instructions
                )

                ext = file.filename.split(".")[-1]
                if ext not in ["py", "md"]:
                    ext = ""
                print(
                    f"file: {file.filename}\n\n```{ext}\n{file.content}\n```",
                    header="dkdc.ai",
                )
                confirm = typer.confirm("write file?")
                if confirm:
                    fs.write_file(file.filename, file.content)
                    response = f"wrote file: {file.filename}..."
                else:
                    response = "file write cancelled..."

            case "context" | "c":
                response = f"context:\n\n{fs.files_to_markdown(client.context)}"
            case "reset" | "r":
                response = "resetting context..."
                client.reset()
            case _:
                response = client(text)
                response = response.choices[0].message.content

        if response:
            print(response, header="dkdc.ai")
