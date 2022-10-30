import requests

class Quote:
  def __init__(self, author: str, content: str):
    self.author: str = author
    self.content: str = content

BASE_URL = "https://api.quotable.io"
PAGE_SIZE = 100

all_quotes: list[Quote] = []
max_num_quotes: int = 100000000000


current_page_num: int = 1
while len(all_quotes) < max_num_quotes:
  print(f"making request for page {current_page_num}, {len(all_quotes)} < {max_num_quotes}")
  resp = requests.get(f"{BASE_URL}/quotes", params={"limit": PAGE_SIZE, "page": current_page_num})
  results = resp.json()
  max_num_quotes = results["totalCount"]
  result_quotes: list[dict[str, str]] = results["results"]
  for thing in result_quotes:
    q: Quote = Quote(thing["author"], thing["content"])
    all_quotes.append(q)
  current_page_num += 1

