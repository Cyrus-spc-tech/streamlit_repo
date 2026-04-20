import os
from exa_py import Exa
from dotenv import load_dotenv
from rich import print


load_dotenv()

class EXAA:
    def __init__(self):
        self.api_key = os.getenv('EXA_API_KEY')
        self.exa = Exa(self.api_key)

    def search_and_print(self):
        search_query = input("Enter your search query: ")

        def print_results(results):
            for result in results.results:
                print(f"[bold cyan]{result.title}[/bold cyan]")
                print(f"[dim]{result.url}[/dim]")
                print(f"[dim]{result.summary}[/dim]")
                print()

        results = self.exa.search_and_contents(
            f"{search_query}",
            text=True,
        )
