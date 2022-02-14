import json, requests

# Load config
config = None
with open("config.json") as f:
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

# Test
response = requests.get("https://mbasic.facebook.com",
                        headers=headers,
                        cookies=cookies)
print(response.content)
