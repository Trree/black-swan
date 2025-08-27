import requests
from typing import List, Dict, Any

class Report:
    def __init__(self, data: Dict[str, Any], report_type: str):
        self.id = data.get("id")
        self.title = data.get("data", {}).get("title") or data.get("data", {}).get("content")
        self.pubDate = data.get("time")
        self.extra = {"info": report_type}
        self.url = f"https://mktnews.net/flashDetail.html?id={self.id}"

def fetch_mktnews():
    url = "https://api.mktnews.net/api/flash/host"
    res = requests.get(url).json()

    categories = ["policy", "AI", "financial"]
    type_map = {"policy": "Policy", "AI": "AI", "financial": "Financial"}

    all_reports = []
    for category in categories:
        # Find the category object
        cat_obj = next((item for item in res["data"] if item["name"] == category), None)
        flash_list = []
        if cat_obj and cat_obj.get("child"):
            flash_list = cat_obj["child"][0].get("flash_list", [])
        for item in flash_list:
            all_reports.append(Report(item, type_map[category]))

    # Sort by pubDate descending (assuming ISO format)
    all_reports.sort(key=lambda r: r.pubDate, reverse=True)

    result = []
    for report in all_reports:
        result.append({
            "id": report.id,
            "title": report.title,
            "pubDate": report.pubDate,
            "extra": report.extra,
            "url": report.url,
        })
    return result

# Example usage:
news = fetch_mktnews()
print(news)