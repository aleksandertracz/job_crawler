import requests
from bs4 import BeautifulSoup
import re
import time
import os
from datetime import datetime

# Function to check if a job link contains any of the keywords
def check_keywords(job_url, kws):
    # Convert job_url to lowercase
    job_url = job_url.lower()
    # Convert kws to lowercase
    kws = [kw.lower() for kw in kws]
    # Check if any of the keywords are in the job url
    for kw in kws:
        if kw in job_url:
            return True
    return False

# Function to fetch the job links
def fetch_job_links(website, no_pages, kws):
    # Initialize the job links list
    job_links = []
    # List URLs of each website
    urls = {
        "eldorado": "https://czyjesteldorado.pl/search?q=&page=",
        "pracuj": "https://it.pracuj.pl/praca?pn="
    }
    # Dict of job url patterns for each website
    job_url_patterns = {
        "eldorado": re.compile(r"^https://czyjesteldorado.pl/praca/\d+-[\w-]+$"),
        "pracuj": re.compile(r"^https://www.pracuj.pl/praca/[\w-]+,oferta,\d+$"),
    }
    # Loop through the pages
    for page in range(no_pages):
        url = f"{urls[website]}{page}"
        response = requests.get(url)
        response.raise_for_status()  # Raise error if something went wrong   
        # Initiate the BeautifulSoup object
        soup = BeautifulSoup(response.text, "html.parser")
        # Regex pattern for job URLs
        job_url_pattern = job_url_patterns[website]
        # Extract all <a> links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if job_url_pattern.match(href) and check_keywords(href, kws):
                job_links.append(href)
        # Polite delay
        time.sleep(10)
    return list(set(job_links))  # Remove duplicates

# Function to read in all job links from the master file
def read_master_file(master_filename):
    with open(master_filename, "r") as f:
        existing_job_links = [line.split(";")[0] for line in f.read().splitlines()]
        f.close()
    return existing_job_links

# Function to add the new job links to the new file if not repeated in the master file
def add_new_job_links(job_links, new_file_path, existing_job_links):
    with open(new_file_path, "w") as f:
        for link in job_links:
            if link not in existing_job_links:
                f.write(f"{link}\n")
        f.close()

# Function to add the new job links to the master file
def add_new_job_links_to_master(job_links, master_file_path, existing_job_links, date):
    with open(master_file_path, "a") as f:
        for link in job_links:
            if link not in existing_job_links:
                f.write(f"{link};{date}\n")
        f.close()

# Function to save the job links to a new file everyday
def save_job_links(job_links, path, filename):
    # Initiate the date of scraping
    today = datetime.now().strftime("%Y-%m-%d")
    # Amend the new filename with the date
    new_filename = f"{filename}_{today}.txt"
    # Initiate the new file full path
    full_path = os.path.join(path, new_filename)
    # Initiate the master file name
    master_filename = f"{filename}_master.txt"
    # Initiate the master file full path
    master_full_path = os.path.join(path, master_filename)
    # If the new file already exists, delete it
    if os.path.exists(full_path):
        os.remove(full_path)
    else:
        pass
    # First read in all job links from the master file
    if os.path.exists(master_full_path):
        existing_job_links = read_master_file(master_full_path)
    else:
        existing_job_links = []
    # Add the new job links to the new file if not repeated in the master file
    add_new_job_links(job_links, full_path, existing_job_links)
    # Add the new job links to the master file
    add_new_job_links_to_master(job_links, master_full_path, existing_job_links, today)

# Run the scraper
if __name__ == "__main__":
    # Set the dictionary of websites to search for
    websites = ["eldorado", "pracuj"]
    # # Set the number of pages to fetch
    pages = 10
    # Set the keywords to search for
    keywords = ["python", "data", "risk", "quant", "quantitative", "analytics"]
    # Set the path to save the job links
    path = "links"
    # Set the filename to save the job links, without the extension
    filename = "job_links"

    for website in websites:
        print(f"Fetching job links from {website}")
        links = fetch_job_links(website, pages, keywords)
        print(f"Found {len(links)} job links")
        # Save the job links to the file
        save_job_links(links, path, filename + "_" + website)
