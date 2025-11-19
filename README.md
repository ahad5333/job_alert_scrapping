````markdown
# Job Alert Dashboard 🚀

**Job Alert Dashboard** is a Python-based web scraping project that automatically fetches the latest job postings from popular UAE job portals like GulfTalent and NaukriGulf. It filters jobs based on specific keywords and displays them in a modern, responsive HTML dashboard that updates every minute.

---

## Features ✨

- Automatically scrapes jobs from multiple sources.
- Filters jobs based on relevant keywords such as:
  `developer, engineer, react, javascript, mern, node, express, frontend, backend, full stack, web developer, software developer, cloud, aws, devops, data analyst, qa, tester, web designer`.
- Highlights new job postings with a modern card UI.
- Auto-refresh countdown every 60 seconds.
- Responsive layout compatible with desktop and mobile.
- Clean, professional design with hover effects.

---

## Tech Stack 🛠️

- **Backend:** Python, Selenium, WebDriver Manager
- **Frontend:** HTML5, CSS3, Google Fonts
- **Automation:** Web scraping from GulfTalent & NaukriGulf
- **Browser Automation:** ChromeDriver (headless mode)

---

## Installation & Setup ⚙️

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/job-alert-dashboard.git
   cd job-alert-dashboard
````

2. **Install dependencies:**

   ```bash
   pip install selenium webdriver-manager
   ```

3. **Ensure Google Chrome is installed** on your system.

4. **Run the Python script:**

   ```bash
   python job_alert.py
   ```

5. **Open the dashboard:**

   * The script generates `latest_jobs.html` in the project folder.
   * Open it in your browser to see the latest jobs.

---

## Project Structure 📂

```
job-alert-dashboard/
│
├── job_alert.py          # Main Python script to scrape and update jobs
├── latest_jobs.html      # Generated HTML dashboard
├── style.css             # Styles for the dashboard
└── README.md             # Project documentation
```

---

## How It Works ⚡

1. The script navigates to each job portal URL.
2. It fetches all job titles and posted dates using CSS selectors.
3. Filters the jobs based on the predefined `FILTER_KEYWORDS`.
4. Checks if the job is new and not already displayed.
5. Appends new jobs to the `latest_jobs.html` dashboard.
6. Updates the dashboard every 60 seconds automatically.

---

## Customization 🎨

* **Keywords:** Modify `FILTER_KEYWORDS` in `job_alert.py` to track different job titles or skills.
* **Check Interval:** Change `CHECK_INTERVAL` to control how often the script checks for new jobs.
* **Sources:** Add or remove job portals by updating the `job_sources` array.

---

## Screenshots 📸

![Dashboard Preview](screenshot.png)

---

## License 📝

This project is open-source and free to use. Feel free to modify and adapt it to your needs.

---

## Contact 📬

**Mohammed Ahadullah**
Email: [ahad53344@gmail.com](mailto:ahad53344@gmail.com)
LinkedIn: [linkedin.com/in/abdul-ahad-962951200](https://linkedin.com/in/abdul-ahad-962951200)
GitHub: [github.com/ahad5333](https://github.com/ahad5333)
Portfolio: [mohammed-ahadullah-portfolio.vercel.app](https://mohammed-ahadullah-portfolio.vercel.app/)

```
