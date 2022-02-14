import json, requests, re, pathlib, time, datetime

from scrapy.selector import Selector

# Load config
config = None
with open("../config.json") as f:
  config = json.load(f)

# Get facebook cookies
cookies_fields = ["c_user", "xs"]
cookies = {}
for field in cookies_fields:
  if field not in config:
    raise Exception("Facebook cookies must have fields: " +
                    ", ".join(cookies_fields))
  cookies[field] = config[field]

# Create headers
headers = {}

# Get User-Agent
if "User-Agent" not in config:
  raise Exception("User-Agent not found")
headers["User-Agent"] = config["User-Agent"]

# Get list of all active friends
def getOnlineFriends():
  current = int(time.time())
  pathlib.Path("data").mkdir(exist_ok=True)
  response = requests.get("https://mbasic.facebook.com/buddylist.php",
                          headers=headers,
                          cookies=cookies)
  sel = Selector(response)
  for node in sel.xpath("//table[@class='m bk ca']/tbody/tr"):
    # Get user information and status
    userInfo = node.xpath("./td[@class='t bl']/a")
    status = node.xpath("./td[@class='n bo']/img")
    # Get fbid, name and online status
    fbid = re.search("\d+", userInfo.attrib["href"]).group()
    name = userInfo.xpath("./text()").get()
    isOnline = (status.attrib["aria-label"] == "Active now")
    # Only online friends
    if isOnline:
      with open("data/" + fbid, "ab") as f:
        f.write((str(current) + "\n").encode("UTF-8"))
        f.write((name + "\n").encode("UTF-8"))

while True:
  getOnlineFriends()
  print("INFO: Finished at " + str(datetime.datetime.now()))
  time.sleep(60 * 5)
