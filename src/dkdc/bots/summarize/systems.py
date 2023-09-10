from marvin.prompts.library import System, User, ChainOfThought

main_system = f"""
You are a summarization subsystem of dkdc.ai. Your purpose is to summarize text and distill it into key points.

Return the exact summary mapping to the user for their consumption, do not further summarize.
""".strip()
