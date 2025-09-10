from typing import List, Dict, Any

import dateparser
import requests
from bs4 import BeautifulSoup


def parse_relative_time(relative_str):
    """
    使用 dateparser 解析相对时间字符串。

    参数:
        relative_str (str): 相对时间字符串。

    返回:
        datetime: 解析得到的绝对时间。
    """
    absolute_time = dateparser.parse(relative_str)
    if absolute_time is None:
        raise ValueError(f"无法解析字符串: {relative_str}")
    return absolute_time

def fetch_gelonghui() :
    base_url = "https://www.gelonghui.com"
    response = requests.get("https://www.gelonghui.com/news/")
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    news_items = []

    for el in soup.select(".article-content"):
        a = el.select_one(".detail-right > a")
        time_p = el.find("p", class_="time")
        if a:
            url = a.get("href")
            title = a.find("h2").get_text(strip=True) if a.find("h2") else ""
            summary_tag = a.find("summary")
            info_text = summary_tag.get_text(strip=True) if summary_tag else None
            if time_p :
                time_spans = time_p.find_all("span")
                time_text_str = time_spans[-1].get_text(strip=True) if time_spans else None
                time_text_p = parse_relative_time(time_text_str)
                time_text = time_text_p.strftime('%Y-%m-%d %H:%M:%S')

            else:
                time_text = ""

            if url and title:
                news_items.append({
                    "title": title,
                    "link": base_url + url,
                    "description": info_text,
                    "pubDate": time_text,
                })
    return {"gelonghui" : news_items}

# 示例用法
if __name__ == "__main__":
    news = fetch_gelonghui()
    for item in news:
        print(item)