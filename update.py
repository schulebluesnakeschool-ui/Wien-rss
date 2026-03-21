import urllib.request
import urllib.parse
import json
from datetime import datetime

def safe_get(url, params=None):
    try:
        if params:
            url = url + "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print("API error:", e)
        return None

# 1. Haltestelle suchen
stop_search = safe_get(
    "https://transport.rest/stops",
    {"query": "Strozzigasse", "results": 1}
)

if not stop_search:
    stop_id = None
else:
    stop_id = stop_search[0]["id"]

# 2. Abfahrten holen
departures = []
if stop_id:
    dep = safe_get(
        f"https://transport.rest/stops/{stop_id}/departures",
        {"duration": 30}
    )
    if dep:
        departures = dep

# 3. Filtern
filtered = []
for dep in departures:
    try:
        if dep["line"]["name"] == "13A" and "Hauptbahnhof" in dep["direction"]:
            filtered.append(dep)
    except:
        pass

# 4. RSS erzeugen
rss_items = ""
for i, dep in enumerate(filtered):
    try:
        when = dep["when"]
        dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
        time_str = dt.strftime("%H:%M:%S")

        rss_items += f"""
        <item>
          <title>13A → Hauptbahnhof um {time_str}</title>
          <description>Abfahrt um {time_str}</description>
          <guid>13A-{i}</guid>
        </item>
        """
    except:
        pass

if not rss_items:
    rss_items = """
    <item>
      <title>Keine Daten</title>
      <description>Keine Abfahrten gefunden</description>
      <guid>none</guid>
    </item>
    """

rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>13A Strozzigasse → Hauptbahnhof</title>
    <link>https://transport.rest</link>
    <description>Echtzeit-Abfahrten des 13A</description>
    <language>de</language>
    {rss_items}
  </channel>
</rss>
"""

with open("13a-strozzigasse-hbf.xml", "w", encoding="utf-8") as f:
    f.write(rss_feed)

print("RSS updated successfully")
