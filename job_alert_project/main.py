# job_search_all.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from datetime import datetime, timedelta
import urllib.parse

# ------------- CONFIG ----------------
CHECK_INTERVAL = 60  # seconds between cycles (adjust as needed)
OUTPUT_FILE = "latest_jobs.html"
FILTER_KEYWORDS = [
    "developer", "engineer", "react", "javascript", "mern", "node", "express",
    "frontend", "backend", "full stack", "web developer", "software developer",
    "software engineer", "react developer", "node developer", "full stack developer",
    "cloud", "aws", "devops", "data", "data analyst", "product data",
    "product analyst", "it support", "technical support", "qa", "tester", "web designer"
]

previous_jobs = set()  # store unique job signatures to prevent duplicates

# ------------- SOURCES -------------
# Each source can use either 'search_url' (preferred), or 'search_box' + 'search_button' for in-page searching.
job_sources = [
    {
        "name": "GulfTalent",
        # GulfTalent sometimes supports a query param URL; fallback to in-page search if needed.
        "search_url": "https://www.gulftalent.com/uae/jobs/search?keywords={q}&location=Dubai",
        "job_selector": "a.job-result__title-link",
        "date_selector": "span.job-result__time",
        "link_prefix": "https://www.gulftalent.com"
    },
    {
        "name": "NaukriGulf",
        # NaukriGulf has search URL pattern (may vary): use query encoded in 'k' parameter (best-effort)
        "search_url": "https://www.naukrigulf.com/jobs-in-dubai?keyword={q}",
        "job_selector": "a.jobTitle",
        "date_selector": "span.postedDate",
        "link_prefix": "https://www.naukrigulf.com"
    },
    {
        "name": "Indeed (UAE)",
        # Indeed supports query params reliably
        "search_url": "https://ae.indeed.com/jobs?q={q}&l=Dubai",
        "job_selector": "a.tapItem, a.jobTitle",
        "date_selector": "span.date, div.job_seen_beacon span",  # multiple fallbacks
        "link_prefix": "https://ae.indeed.com"
    },
    {
        "name": "Bayt",
        # Bayt query—best-effort pattern (may require tuning)
        "search_url": "https://www.bayt.com/en/uae/jobs/?q={q}&l=Dubai",
        "job_selector": "a.job-link, a.jobTitle",
        "date_selector": "span.postedDate, time",
        "link_prefix": "https://www.bayt.com"
    },
    {
        "name": "Laimoon",
        # Laimoon search URL pattern (best-effort)
        "search_url": "https://laimoon.com/jobs/search?keywords={q}&location=Dubai",
        "job_selector": "a.job-link, .job-card a",
        "date_selector": ".job-posted, span.time",
        "link_prefix": "https://laimoon.com"
    },
    {
        "name": "MonsterGulf",
        # Monster Gulf best-effort search URL
        "search_url": "https://www.monstergulf.com/search/?q={q}&where=Dubai",
        "job_selector": "a.title, a.companyname",
        "date_selector": "time, span.date",
        "link_prefix": ""
    }
]

# ------------- UTILITIES -------------
def safe_find_text(elem):
    try:
        return elem.text.strip()
    except:
        return ""

def parse_posted_time(text):
    """Simple parse for common relative times like '3 hours ago', '2 days ago', 'just posted'"""
    now = datetime.now()
    if not text:
        return now - timedelta(days=999)
    t = text.lower()
    try:
        if "just" in t or "today" in t:
            return now
        if "hour" in t:
            num = int([s for s in t.split() if s.isdigit()][0])
            return now - timedelta(hours=num)
        if "minute" in t:
            num = int([s for s in t.split() if s.isdigit()][0])
            return now - timedelta(minutes=num)
        if "day" in t:
            num = int([s for s in t.split() if s.isdigit()][0])
            return now - timedelta(days=num)
    except:
        # fallback
        return now - timedelta(days=999)
    return now - timedelta(days=999)

def initialize_html():
    base_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Latest Job Alerts</title>
<link rel="stylesheet" href="style.css">
<script>
let timeLeft = {CHECK_INTERVAL};
setInterval(() => {{
    const el = document.getElementById('countdown');
    if (el) el.innerText = "Next refresh in " + timeLeft + " seconds";
    timeLeft--;
    if (timeLeft <= 0) location.reload();
}}, 1000);
</script>
</head>
<body>
<h2>Job Alert Dashboard</h2>
<div id="countdown">Next refresh in {CHECK_INTERVAL} seconds</div>
<div id="job-container"></div>
</body>
</html>"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(base_html)

def append_jobs_to_file(jobs, source_name):
    if not jobs:
        return
    block = f"<h3>{source_name} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h3>\n<ul class='job-list'>\n"
    for (title, link, posted) in jobs:
        # Unique signature to track duplicates
        sig = f"{title}||{link}"
        if sig in previous_jobs:
            continue
        previous_jobs.add(sig)
        block += f"<li class='new-job'><a href='{link}' target='_blank'>{title}</a><span>{posted}</span></li>\n"
    block += "</ul>\n<hr>\n"

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        start_tag = "<div id=\"job-container\">"
        idx = content.find(start_tag)
        if idx == -1:
            # fallback: append at end
            new_content = content + "\n" + block
        else:
            insert_pos = idx + len(start_tag)
            new_content = content[:insert_pos] + "\n" + block + content[insert_pos:]
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print("Error updating HTML:", e)

# ------------- SCRAPING ----------------
def fetch_from_search_url(driver, source, keyword, last_check):
    """Load a constructed search URL and scrape results."""
    q = urllib.parse.quote_plus(keyword)
    search_url = source.get("search_url")
    if not search_url:
        return []

    url = search_url.format(q=q)
    try:
        driver.get(url)
    except Exception as e:
        print(f"Failed to open {url}: {e}")
        return []

    # Wait a bit for content to load (some sites lazy-load)
    try:
        WebDriverWait(driver, 8).until(lambda d: d.find_elements(By.CSS_SELECTOR, source["job_selector"]))
    except TimeoutException:
        # might still find some items without waiting
        pass

    titles = driver.find_elements(By.CSS_SELECTOR, source["job_selector"])
    dates = driver.find_elements(By.CSS_SELECTOR, source["date_selector"])
    results = []

    # Zip safest: if counts mismatch we'll iterate by titles and attempt to get a date near it
    for i, t in enumerate(titles):
        try:
            title = safe_find_text(t)
            link = t.get_attribute("href") or ""
            if link.startswith("/"):
                link = (source.get("link_prefix") or "") + link

            # Filtering by keyword presence in title still helps reduce noise
            if not any(k in title.lower() for k in FILTER_KEYWORDS):
                continue

            # try to pick corresponding date, if available
            date_text = ""
            if i < len(dates):
                date_text = safe_find_text(dates[i])
            else:
                # try to find a date element relative to the title element
                try:
                    parent = t.find_element(By.XPATH, "./ancestor::div[1]")
                    date_el = parent.find_element(By.CSS_SELECTOR, source["date_selector"])
                    date_text = safe_find_text(date_el)
                except Exception:
                    date_text = ""

            posted_time = parse_posted_time(date_text)
            if posted_time > last_check:
                results.append((title, link, date_text or ""))
        except Exception:
            continue
    return results

# ------------- MAIN --------------
def create_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")  # use new headless if supported
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def run():
    print("Initializing driver...")
    # Set headless=False for debugging if you see no results.
    driver = create_driver(headless=True)
    initialize_html()
    print("Dashboard initialized ->", OUTPUT_FILE)

    last_check = datetime.now() - timedelta(minutes=30)  # collect recent jobs on first run
    try:
        while True:
            cycle_start = datetime.now()
            for source in job_sources:
                all_found = []
                print(f"\n--- Searching {source['name']} ---")
                for keyword in FILTER_KEYWORDS:
                    print(" Searching keyword:", keyword)
                    results = fetch_from_search_url(driver, source, keyword, last_check)
                    if results:
                        print(f"  -> {len(results)} results for '{keyword}' on {source['name']}")
                        all_found.extend(results)
                    # polite pause between keyword searches to avoid being flagged
                    time.sleep(1.0)

                # Deduplicate within this source cycle by link
                dedup = []
                seen_links = set()
                for r in all_found:
                    if r[1] and r[1] not in seen_links:
                        dedup.append(r)
                        seen_links.add(r[1])

                if dedup:
                    append_jobs_to_file(dedup, source["name"])
                    print(f" Appended {len(dedup)} new jobs from {source['name']}")
                else:
                    print(f" No new jobs found on {source['name']}")

            last_check = datetime.now()
            elapsed = (datetime.now() - cycle_start).total_seconds()
            sleep_for = max(0, CHECK_INTERVAL - elapsed)
            print(f"\nCycle complete. Sleeping {sleep_for:.1f}s ...")
            time.sleep(sleep_for)
    finally:
        print("Shutting down driver...")
        driver.quit()

if __name__ == "__main__":
    run()
