# imports
import uuid
import typer

from datetime import datetime
from dkdc.utils import filesystem as fs
from dkdc.ai.models import File
from dkdc.ai.openai import Client
from dkdc.cli.console import print
from dkdc.utils.database import connect, TABLES


# functions
def _write_data(con, data: dict) -> None:
    """
    write data to database
    """
    # print(f"{data}")
    if TABLES["dkdc"] not in con.list_tables():
        con.create_table(TABLES["dkdc"], data)
    else:
        con.insert(TABLES["dkdc"], data)


def run_ai() -> None:
    """
    chat with ai
    """
    con = connect()
    client = Client()
    session_id = str(uuid.uuid4())
    print("starting dkdc.ai...")

    while True:
        data = {
            "session_id": [session_id],
            "datetime": [datetime.now().isoformat()],
            "step_id": [str(uuid.uuid4())],
            "input": [None],
            "start": [None],
            "action": [None],
            "response": [None],
            "usage": [{"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}],
        }

        response = None
        text = typer.prompt("user").strip()
        print(text, header="user")
        data["input"] = [text]

        start = text.split()[0]
        data["start"] = [start]

        match start:
            # exit
            case "exit" | "e" | "quit" | "q":
                data["action"] = ["exit"]
                response = "exiting dkdc.ai..."
                print("exiting dkdc.ai...")
                break
            # load (files into context)
            case "load" | "l":
                data["action"] = ["load"]
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
            # write (file(s) to disk)
            case "write" | "w":
                data["action"] = ["write"]
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
            # context (show context)
            case "context" | "c":
                data["action"] = ["context"]
                response = f"context:\n\n{fs.files_to_markdown(client.context)}"
            # reset (reset message history and context)
            case "reset" | "r":
                data["action"] = ["reset"]
                client.reset()
                response = "reset context..."
            # default (chat response)
            case _:
                data["action"] = ["chat"]
                response = client(text)
                usage = response.usage
                data["usage"] = [usage.dict()]
                # data["full_response"] = [response.dict()] # TODO: Ibis bug?
                response = response.choices[0].message.content

        data["response"] = [response]
        if response:
            print(response, header="dkdc.ai")
        _write_data(con, data)

    con.disconnect()
    client.reset()
    print(response)
