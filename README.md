# Flight Price Analyzer Bot & Dashboard

An advanced, stealth-enabled Python bot that performs geographical radius searches to find the cheapest flights across multiple nearby airports. Built for speed and reliability, it bypasses basic bot protections and visualizes the results on a beautiful dark-mode dashboard.

## 🚀 The Optimization Journey

Originally, this bot executed 99 flight queries sequentially, taking **~115 minutes** (70s per query). 

We optimized the execution time down to **~35 minutes** by implementing concurrent headless browser scraping:
1. **Initial attempt (Failed):** We used Python's `ThreadPoolExecutor`. However, Playwright's Sync API utilizes the main thread's asyncio event loop under the hood, leading to `I/O operation on closed pipe` race conditions when threads tried to close contexts simultaneously.
2. **Final Solution (Success):** We rewrote the scraper to natively use `playwright.async_api` and `asyncio`. By using `asyncio.Semaphore(3)`, we safely ran 3 concurrent stealth Chromium browsers, perfectly parallelizing the network I/O without thread safety issues.

## 🛠 Features

- **Radius Search:** Provide a target destination and a radius (e.g., 200km) — the bot automatically finds all airports within that radius and checks flights for them.
- **Stealth Scraper:** Uses `playwright-stealth` (v2 async API) to avoid detection by airline aggregators.
- **Smart Date Sampling:** Automatically generates search dates covering weekends and weekdays over a 60-day window.
- **Beautiful Dashboard:** A Flask-powered web UI featuring dark mode, glassmorphism, and live interactive data tables.
- **Excel/CSV Export:** Automatically dumps results to neatly formatted spreadsheets.

## 💻 Installation

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install flask pandas openpyxl geopy amadeus playwright playwright-stealth
   ```
3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## 🎮 Usage

**Step 1: Run the Bot**
```bash
python flight_price_analyzer.py
```
This will run the headless browsers and dump the results into the `flight_results/` directory.

**Step 2: Launch the Dashboard**
```bash
python app.py
```
Open `http://localhost:5000` in your browser to view the beautiful interactive dashboard!

---
*Disclaimer: Web scraping Google Flights is for personal educational use only. Do not use commercially.*
