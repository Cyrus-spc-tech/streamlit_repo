import os
from exa_py import Exa
from dotenv import load_dotenv
from rich import print
load_dotenv()


api_key = os.getenv('EXA_API_KEY')

exa = Exa(api_key)

search_query = input("Enter your search query: ")

def print_results(results):
    for result in results.results:
        print(f"[bold cyan]{result.title}[/bold cyan]")
        print(f"[dim]{result.url}[/dim]")
        print(f"[dim]{result.summary}[/dim]")
        print()


results = exa.search_and_contents(
    f"{search_query}",
    text=True
)

print_results(results)
