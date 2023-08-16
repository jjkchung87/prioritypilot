import requests
from bs4 import BeautifulSoup
import json

# URL of the page containing the script
url = "http://www.pgatour.com/players"

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Find the script tag containing the JSON data
script_tag = soup.find("script", {"id": "__NEXT_DATA__"})

# Extract the JSON data from the script tag
json_data = json.loads(script_tag.contents[0])

# Access the golfer information
golfer_images = json_data["props"]["pageProps"]["players"]["players"]

# final_golfers = []

# # Extract and print id, name, and image URL for each golfer
# for golfer in golfers:
#     golfer_id = golfer["id"]
#     golfer_name = golfer["displayName"]
#     image_url = golfer["headshot"]

#     final_golfer = {"golfer_id":int(golfer_id), 
#                     "golfer_name":golfer_name, 
#                     "image_url": image_url}
#     final_golfers.append(final_golfer)


