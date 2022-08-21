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

# Get all friends of a profile
def get_profile_friends(uid):
  friend_url = "https://mbasic.facebook.com/"
  # Profile UID number
  if uid.isdigit():
    friend_url += "profile.php?id=" + uid + "&v=friends"
  # Profile username
  else:
    friend_url += uid + "/friends"

  isMore = True
  ret = []
  while isMore:
    time.sleep(20)
    response = requests.get(friend_url, headers=headers, cookies=cookies)
    block_sign = "You’re Temporarily Blocked"
    if block_sign in response.text:
      raise Exception(block_sign)

    sel = Selector(response)
    isMore = False
    for node in sel.xpath("//a"):
      if "href" not in node.attrib:
        continue
      href = node.attrib["href"]
      o = parse.urlparse(href)
      path = o.path
      query = o.query

      friend_sign = "fref=fr_tab"
      if friend_sign in href:
        if path == "/profile.php":
          param = parse.parse_qs(query)
          if "id" in param:
            fbid = param["id"][0]
          else:
            # Owner FBID
            fbid = config["c_user"]
        else:
          fbid = path[1:]
        ret.append(fbid)

      more_sign_1 = "unit_cursor"
      more_sign_2 = "mbasic.facebook.com"
      if (more_sign_1 in href) and (more_sign_2 not in href):
        friend_url = "https://mbasic.facebook.com" + href
        isMore = True
  return ret

# Load data
with open("network.json") as f:
  network = json.load(f)

# Run queue
while len(network["queue"]):
  it = network["queue"].pop(0)
  uid = it[0]
  ref_index = it[1]

  if uid in network["vertices"]:
    uid_index = network["vertices"][uid]
    if [ref_index, uid_index] not in network["edges"]:
      network["edges"].append([ref_index, uid_index])
    continue

  uid_index = len(network["vertices"])
  network["vertices"][uid] = uid_index

  friend_list = get_profile_friends(uid)
  for friend in friend_list:
    if friend in network["vertices"]:
      friend_index = network["vertices"][friend]
      network["edges"].append([friend_index, uid_index])
    else:
      network["queue"].append([friend, uid_index])
  if [ref_index, uid_index] not in network["edges"]:
    network["edges"].append([ref_index, uid_index])

  with open("network.json", "w") as f:
    json.dump(network, f)
  print("INFO: DONE uid={}".format(uid))
