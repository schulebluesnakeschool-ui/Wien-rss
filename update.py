import urllib.request
import json
from datetime import datetime

STOP_ID = "4081"  # Strozzigasse/Zieglergasse Richtung Hauptbahnhof

def get_data():
    url = f"https://www.wienerlinien.at/ogd_realtime/monitor?stopId={STOP_ID}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))

data = get_data()

items = data["data"]["monitors"][0]["lines"]

rss_items = ""

for i, line in enumerate(items):
    if line["name"] == "13A" and "Hauptbahnhof" in line["towards"]:
        for dep in line["departures"]["departure"]:
            try:
                time = dep["departureTime"]["timeReal"]
                dt = datetime.fromtimestamp(time / 1000)
                t = dt.strftime("%H:%M:%S")

                rss_items += f"""
                <item>
                  <title>13A → Hauptbahnhof um {t}</title>
                  <description>Abfahrt um {t}</description>
                  <guid>{t}-{i}</guid>
                </item>
                """
            except:
                pass

if not rss_items:
    now = datetime.now().strftime("%H:%M:%S")
    rss_items = f"""
    <item>
      <title>Keine Daten ({now})</title>
      <description>Keine Abfahrten gefunden</description>
      <guid>{now}</guid>
    </item>
    """

rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>13A Strozzigasse → Hauptbahnhof</title>
    <link>https://www.wienerlinien.at</link>
    <description>Echtzeit-Abfahrten des 13A</description>
    <language>de</language>
    {rss_items}
  </channel>
</rss>
"""

with open("13a-strozzigasse-hbf.xml", "w", encoding="utf-8") as f:
    f.write(rss_feed)

print("RSS updated successfully")
