import json, requests, time

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

# Only support "m.facebook.com"
# Only support story + photo
# Only support general reactions (ignore the detail of each type)
with open("reactions.json") as f:
  reactions = json.load(f)
def getReactions(sel):
  for node in sel.xpath("//a[@class='darkTouch _1aj5 l']"):
    # Extract fbid
    o = parse.urlparse(node.attrib["href"])
    path = o.path
    query = o.query
    if path == "/profile.php":
      param = parse.parse_qs(query)
      if "id" in param:
        fbid = parse.parse_qs(query)["id"][0]
      else:
        fbid = ""
    else:
      fbid = path[1:]
    # Do something with fbid
    if fbid in reactions:
      reactions[fbid] += 1
    else:
      reactions[fbid] = 1
def getMoreReactions(href, is_first):
  time.sleep(10)
  response = requests.get("https://m.facebook.com{}".format(href),
                          headers=headers, cookies=cookies)
  print('.', end='')
  href = ""
  if is_first:
    sel = Selector(response)
    getReactions(sel)
    node = sel.xpath("//a[@class='touchable primary']")
    if node:
      href = node.attrib["href"]
  else:
    actions = json.loads(response.text[9:])["payload"]["actions"]
    for act in actions:
      if ("target" not in act) or ("html" not in act):
        continue
      sel = Selector(text = act["html"])
      # reaction_profile_browser
      if act["target"] == "reaction_profile_browser":
        getReactions(sel)
      # other
      else:
        node = sel.xpath("//a[@class='touchable primary']")
        if node:
          href = node.attrib["href"]
  return href, False
def getAllReactions(href):
  time.sleep(10)
  response = requests.get("https://m.facebook.com{}".format(href),
                          headers=headers, cookies=cookies)
  print('.', end='')
  txt = response.text.replace('<!--', '<').replace('-->', '>')
  sel = Selector(text=txt)
  node = sel.xpath("//div[@class='_52jh _5ton _45m7']/a")
  if node:
    href, is_first = node.attrib["href"], True
    while href:
      href, is_first = getMoreReactions(href, is_first)

# href: /story.php?story_fbid=&id=
# href: /photo.php?fbid=&id=
with open(input("Input 'href' file: ")) as f:
  l = f.read().splitlines()
for href in l:
  if href:
    try:
      getAllReactions(href)
      with open("reactions.json", "w") as f:
        json.dump(reactions, f)
      print("Succeed at href: {}".format(href))
    except:
      print("Error at href: {}".format(href))
      raise
for key, value in sorted(reactions.items(), key=lambda item: item[1]):
  print("{0:30} {1}".format(key, value))
