# https://github.com/DIYgod/RSSHub/blob/master/lib/routes/cls/utils.ts
import hashlib
from urllib.parse import urlencode

root_url = 'https://www.cls.cn'

params = {
    'appName': 'CailianpressWeb',
    'os': 'web',
    'sv': '7.7.5'
}

def get_search_params(more_params):
    # Merge params and more_params
    combined = {**params, **more_params}
    # Sort by key
    sorted_items = sorted(combined.items())
    # Encode as query string
    query_string = urlencode(sorted_items)
    # SHA1 hash, then MD5 hash of the SHA1 hex digest
    sha1_digest = hashlib.sha1(query_string.encode('utf-8')).hexdigest()
    md5_digest = hashlib.md5(sha1_digest.encode('utf-8')).hexdigest()
    # Append sign
    result_params = dict(sorted_items)
    result_params['sign'] = md5_digest
    return result_params

def get_cls_header() :
    headers = {
        'accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    return headers