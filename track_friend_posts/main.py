import json, requests

from urllib import parse
from scrapy.selector import Selector

# Load config
config = None
with open("../config.json") as f:
  config = json.load(f)

# Get facebook cookies
fb_cookies_fields = ["c_user", "xs"]
cookies = {}
for field in fb_cookies_fields:
  if field not in config:
    raise Exception("Facebook cookies must have fields: " +
                    ", ".join(fb_cookies_fields))
  cookies[field] = config[field]

# Create headers
headers = {}

# Get User-Agent
if "User-Agent" not in config:
  raise Exception("User-Agent not found")
headers["User-Agent"] = config["User-Agent"]

# Get all posts of my friend
story = []
photo = []
other = []
def getPosts(sel):
  for node in sel.xpath("//footer/div[2]"):
    for subnode in node.xpath("./a"):
      if subnode.xpath("./text()").get() != "Full Story":
        continue
      href = subnode.attrib["href"]
      href_parse = parse.parse_qs(parse.urlparse(href).query)
      if "story_fbid" in href_parse: # normal posts
        txt = "https://mbasic.facebook.com/story.php?story_fbid={}&id={}"
        story.append(txt.format(href_parse["story_fbid"][0],
                                href_parse["id"][0]))
        continue
      if "fbid" in href_parse: # photo posts
        txt = "https://mbasic.facebook.com/photo.php?fbid={}&id={}"
        photo.append(txt.format(href_parse["fbid"][0],
                                href_parse["id"][0]))
        continue
      other.append("https://mbasic.facebook.com{}".format(href)) # other posts
def getMorePosts(href):
  response = requests.get("https://mbasic.facebook.com{}".format(href),
                          headers=headers, cookies=cookies)
  sel = Selector(response)
  getPosts(sel)
  node = sel.xpath("//div[@id='structured_composer_async_container']/div/a")
  href = node.attrib["href"]
  if node.xpath("./span/text()").get() != "See More Stories":
    href = ""
  return href
def getAllPosts(uid):
  href = "/{}".format(uid)
  while href:
    href = getMorePosts(href)

uid = input("User ID: ")
getAllPosts(uid)

with open("story.txt", "w") as f:
  f.write("\n".join(story))
with open("photo.txt", "w") as f:
  f.write("\n".join(photo))
with open("other.txt", "w") as f:
  f.write("\n".join(other))
