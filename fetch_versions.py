import urllib.request
import json
import re

packages = {
    "requests": "2.32",
    "beautifulsoup4": "4.12",
    "yt-dlp": "2025",
    "pydantic": "2.9",
    "PyYAML": "6.0",
    "sentence-transformers": "2.7",
    "rapidfuzz": "3.9",
    "openai": "1.40",
    "Jinja2": "3.1",
    "pytest": "8.3",
    "ruff": "0.6",
    "markdownify": "0.13",
    "mypy": "1.11"
}

results = {}

for pkg, prefix in packages.items():
    try:
        url = "https://pypi.org/pypi/" + pkg + "/json"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            versions = list(data["releases"].keys())
            matching = [v for v in versions if v.startswith(prefix + ".")]
            if not matching and prefix in versions:
                matching = [prefix]
            
            if matching:
                def sort_key(v):
                    parts = []
                    for x in v.split("."):
                        try:
                            parts.append(int(re.sub(r"\D", "", x)))
                        except:
                            parts.append(0)
                    return parts
                matching.sort(key=sort_key)
                results[pkg] = matching[-1]
            else:
                results[pkg] = prefix + ".0"
    except Exception as e:
        results[pkg] = prefix + ".0"

try:
    url = "https://pypi.org/pypi/scikit-learn/json"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        results["scikit-learn"] = data["info"]["version"]
except:
    results["scikit-learn"] = "1.5.2"

try:
    url = "https://pypi.org/pypi/pytest-cov/json"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        results["pytest-cov"] = data["info"]["version"]
except:
    results["pytest-cov"] = "5.0.0"

for k, v in results.items():
    print(k + "==" + v)
