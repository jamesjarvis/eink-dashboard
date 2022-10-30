import requests
import json

class Quote:
  def __init__(self, author: str, content: str):
    self.author: str = author
    self.content: str = content

all_quotes: list[Quote] = []

# Fetch all quotes.

BASE_URL = "https://api.quotable.io"
PAGE_SIZE = 100
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

# Export list of quotes.
with open("quotes", "a") as f:
  for i in range(len(all_quotes)-1):
    q = all_quotes[i]
    json.dump(vars(q), f)
    if i < len(all_quotes):
      f.write('\n')

# Export length of quotes, used for quicker random lookups.
with open("quotes_len", "w") as f:
  f.write(str(len(all_quotes)))

