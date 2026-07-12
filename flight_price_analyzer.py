"""
FLIGHT PRICE ANALYZER BOT - RADIUS SEARCH EDITION
by Antigravity AI | Python 3.9+

INSTALLATION:
    pip install amadeus geopy pandas openpyxl requests
    pip install playwright playwright-stealth
    playwright install chromium

USAGE:
    python flight_price_analyzer.py
"""

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 1 - CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

CONFIG = {
    # Origin airport IATA code (your departure city)
    "ORIGIN_AIRPORT": "LKO",            # Lucknow

    # Target holiday destination (city name or "lat,lon")
    "TARGET_DESTINATION": "New Delhi, India",

    # Search radius (km) around the target destination
    # 200 km captures DEL (12 km), AGR (177 km), DEH (198 km) for Delhi
    "RADIUS_KM": 200,

    # Passengers
    "ADULTS": 1,

    # Cabin class: ECONOMY | PREMIUM_ECONOMY | BUSINESS | FIRST
    "CABIN_CLASS": "ECONOMY",

    # Max results per (date, airport) query
    "MAX_RESULTS_PER_QUERY": 5,

    # Date sampling interval (days). 7 = weekly. 3 = every 3 days (more thorough).
    "DATE_INTERVAL_DAYS": 7,

    # Also check all Fri/Sat/Sun departures?
    "INCLUDE_WEEKENDS": True,

    # Sleep between requests inside each worker (seconds)
    "SLEEP_MIN": 2.0,
    "SLEEP_MAX": 4.0,

    # Parallel workers.
    # Option B (Playwright): 3 is safe. Each worker = 1 browser instance.
    # Option A (Amadeus):    5 is safe. HTTP client is thread-safe.
    "PARALLEL_WORKERS": 3,

    # Data source: "A" = Amadeus API (fast, no IP ban risk)
    #              "B" = Playwright scraper (no API key needed)
    "DATA_SOURCE": "B",

    # Output: "excel" | "csv" | "both"
    "OUTPUT_FORMAT": "both",
    "OUTPUT_DIR": "flight_results",

    # Amadeus credentials (Option A only)
    # Free signup at https://developers.amadeus.com/
    "AMADEUS_API_KEY":    "YOUR_AMADEUS_API_KEY_HERE",
    "AMADEUS_API_SECRET": "YOUR_AMADEUS_API_SECRET_HERE",
    "AMADEUS_HOSTNAME":   "test",   # "test" for sandbox, "production" for live

    "CURRENCY": "INR",
}

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 2 - INDIAN AIRPORTS DATABASE
# ─────────────────────────────────────────────────────────────────────────────

INDIAN_AIRPORTS = [
    # (IATA, Full Name, Lat, Lon, State)
    ("DEL", "Indira Gandhi International Airport",           28.5562, 77.1000, "Delhi"),
    ("BOM", "Chhatrapati Shivaji Maharaj International",     19.0896, 72.8656, "Maharashtra"),
    ("BLR", "Kempegowda International Airport",              13.1986, 77.7066, "Karnataka"),
    ("MAA", "Chennai International Airport",                 12.9900, 80.1693, "Tamil Nadu"),
    ("CCU", "Netaji Subhash Chandra Bose International",     22.6547, 88.4467, "West Bengal"),
    ("HYD", "Rajiv Gandhi International Airport",            17.2313, 78.4298, "Telangana"),
    ("AMD", "Sardar Vallabhbhai Patel International",        23.0772, 72.6347, "Gujarat"),
    ("COK", "Cochin International Airport",                  10.1520, 76.4019, "Kerala"),
    ("TRV", "Trivandrum International Airport",               8.4821, 76.9201, "Kerala"),
    ("PNQ", "Pune Airport",                                  18.5822, 73.9197, "Maharashtra"),
    ("GOI", "Goa International Airport (Dabolim)",           15.3808, 73.8314, "Goa"),
    ("LKO", "Chaudhary Charan Singh International",          26.7606, 80.8893, "Uttar Pradesh"),
    ("VNS", "Lal Bahadur Shastri Airport (Varanasi)",        25.4524, 82.8593, "Uttar Pradesh"),
    ("AGR", "Agra Airport",                                  27.1558, 77.9609, "Uttar Pradesh"),
    ("IXD", "Allahabad Airport",                             25.4401, 81.7339, "Uttar Pradesh"),
    ("KNU", "Kanpur Airport",                                26.4044, 80.3648, "Uttar Pradesh"),
    ("GOP", "Gorakhpur Airport",                             26.7397, 83.4497, "Uttar Pradesh"),
    ("DEH", "Dehradun (Jolly Grant) Airport",                30.1895, 78.1803, "Uttarakhand"),
    ("PGH", "Pantnagar Airport",                             29.0334, 79.4737, "Uttarakhand"),
    ("GAU", "Lokpriya Gopinath Bordoloi Airport",            26.1061, 91.5859, "Assam"),
    ("IXB", "Bagdogra Airport",                              26.6812, 88.3286, "West Bengal"),
    ("JAI", "Jaipur International Airport",                  26.8242, 75.8122, "Rajasthan"),
    ("JDH", "Jodhpur Airport",                               26.2511, 73.0489, "Rajasthan"),
    ("UDR", "Maharana Pratap Airport (Udaipur)",             24.6177, 73.8961, "Rajasthan"),
    ("ATQ", "Sri Guru Ram Dass Jee International",           31.7096, 74.7973, "Punjab"),
    ("LUH", "Ludhiana Airport",                              30.8547, 75.9526, "Punjab"),
    ("IXC", "Chandigarh Airport",                            30.6735, 76.7885, "Chandigarh"),
    ("SXR", "Sheikh ul Alam Airport (Srinagar)",             33.9871, 74.7742, "J&K"),
    ("IXL", "Kushok Bakula Rimpochhe Airport (Leh)",         34.1359, 77.5465, "Ladakh"),
    ("DHM", "Gaggal Airport (Dharamshala/Kangra)",           32.1651, 76.2634, "Himachal Pradesh"),
    ("KUU", "Bhuntar Airport (Kullu-Manali)",                31.8767, 77.1544, "Himachal Pradesh"),
    ("SHL", "Shillong Airport",                              25.7036, 91.9787, "Meghalaya"),
    ("IXS", "Silchar Airport",                               24.9129, 92.9787, "Assam"),
    ("IMF", "Imphal International Airport",                  24.7600, 93.8967, "Manipur"),
    ("PAT", "Jay Prakash Narayan International (Patna)",     25.5913, 85.0880, "Bihar"),
    ("BHO", "Raja Bhoj Airport (Bhopal)",                    23.2875, 77.3374, "Madhya Pradesh"),
    ("IDR", "Devi Ahilyabai Holkar Airport (Indore)",        22.7218, 75.8011, "Madhya Pradesh"),
    ("RPR", "Swami Vivekananda Airport (Raipur)",            21.1804, 81.7388, "Chhattisgarh"),
    ("VGA", "Vijayawada Airport",                            16.5304, 80.7965, "Andhra Pradesh"),
    ("VTZ", "Vishakhapatnam Airport",                        17.7212, 83.2245, "Andhra Pradesh"),
    ("IXE", "Mangalore International Airport",               12.9613, 74.8901, "Karnataka"),
    ("HBX", "Hubli Airport",                                 15.3617, 75.0849, "Karnataka"),
    ("CJB", "Coimbatore International Airport",              11.0300, 77.0434, "Tamil Nadu"),
    ("TIR", "Tirupati Airport",                              13.6325, 79.5433, "Andhra Pradesh"),
    ("IXM", "Madurai Airport",                                9.8345, 78.0934, "Tamil Nadu"),
    ("IXA", "Maharaja Bir Bikram Airport (Agartala)",        23.8869, 91.2404, "Tripura"),
    ("DIB", "Dibrugarh Airport",                             27.4839, 95.0169, "Assam"),
    ("JRH", "Jorhat Airport",                                26.7315, 94.1755, "Assam"),
    ("BBI", "Biju Patnaik International (Bhubaneswar)",      20.2444, 85.8178, "Odisha"),
    ("IXR", "Birsa Munda Airport (Ranchi)",                  23.3143, 85.3217, "Jharkhand"),
    ("BHU", "Bhavnagar Airport",                             21.7522, 72.1852, "Gujarat"),
    ("RAJ", "Rajkot Airport",                                22.3092, 70.7796, "Gujarat"),
    ("STV", "Surat Airport",                                 21.1141, 72.7418, "Gujarat"),
]

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 3 - IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

import os
import sys
import time
import random
import logging
import traceback
from datetime import date, timedelta, datetime
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("ERROR: pandas not found. Run: pip install pandas openpyxl")

try:
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
except ImportError:
    sys.exit("ERROR: geopy not found. Run: pip install geopy")

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 4 - LOGGING (ASCII-only to work on Windows cp1252)
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("flight_bot.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("FlightBot")

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 5 - GEOGRAPHICAL RADIUS SEARCH ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class RadiusSearchEngine:
    def __init__(self, airport_db: list):
        self.airport_db = airport_db
        self._geocoder  = Nominatim(user_agent="flight_price_analyzer_bot_v2")

    def resolve_coordinates(self, destination: str) -> tuple:
        parts = destination.strip().split(",")
        if len(parts) == 2:
            try:
                lat, lon = float(parts[0].strip()), float(parts[1].strip())
                log.info(f"Using direct coordinates: ({lat:.4f}, {lon:.4f})")
                return lat, lon
            except ValueError:
                pass
        log.info(f"Geocoding: '{destination}' ...")
        try:
            loc = self._geocoder.geocode(destination, timeout=10)
            if loc is None:
                raise ValueError(f"No results for '{destination}'")
            log.info(f"Geocoded to: {loc.address[:70]} -> ({loc.latitude:.4f}, {loc.longitude:.4f})")
            return loc.latitude, loc.longitude
        except Exception as e:
            raise RuntimeError(f"Geocoding failed: {e}") from e

    def find_airports_in_radius(self, lat: float, lon: float, radius_km: float) -> list:
        target = (lat, lon)
        found  = []
        for iata, name, alat, alon, state in self.airport_db:
            dist = geodesic(target, (alat, alon)).kilometers
            if dist <= radius_km:
                found.append({"iata": iata, "name": name, "lat": alat,
                              "lon": alon, "state": state, "dist_km": round(dist, 1)})
        found.sort(key=lambda x: x["dist_km"])
        return found

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 6 - SMART DATE SAMPLING
# ─────────────────────────────────────────────────────────────────────────────

def generate_search_dates(interval_days: int = 7, window_days: int = 60,
                          include_weekends: bool = True) -> list:
    today    = date.today()
    end_date = today + timedelta(days=window_days)
    dates    = set()
    cur = today + timedelta(days=1)
    while cur <= end_date:
        dates.add(cur)
        cur += timedelta(days=interval_days)
    if include_weekends:
        d = today + timedelta(days=1)
        while d <= end_date:
            if d.weekday() in (4, 5, 6):
                dates.add(d)
            d += timedelta(days=1)
    sorted_dates = sorted(dates)
    log.info(f"Generated {len(sorted_dates)} search dates "
             f"({today + timedelta(days=1)} to {end_date})")
    return sorted_dates

# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: price extraction
# ─────────────────────────────────────────────────────────────────────────────

def _extract_best_price(text: str) -> float:
    import re
    candidates = re.findall(r"[\d,]+", str(text))
    prices = []
    for c in candidates:
        try:
            v = float(c.replace(",", ""))
            if 500 <= v <= 200_000:
                prices.append(v)
        except ValueError:
            continue
    return min(prices) if prices else 0.0

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 7A - AMADEUS API FETCHER (Option A)
# ─────────────────────────────────────────────────────────────────────────────

class AmadeusFlightFetcher:
    """
    Wraps Amadeus Flight Offers Search v2.
    Free tier: 2000 calls/month. Sign up at https://developers.amadeus.com/
    """
    def __init__(self, api_key: str, api_secret: str, hostname: str = "test"):
        try:
            from amadeus import Client, ResponseError
            self._ResponseError = ResponseError
        except ImportError:
            sys.exit("ERROR: amadeus not found. Run: pip install amadeus")
        self._client = Client(client_id=api_key, client_secret=api_secret,
                              hostname=hostname, log_level="silent")
        log.info(f"Amadeus client ready (hostname={hostname})")

    def fetch(self, origin: str, destination: str, departure_date,
              adults: int = 1, cabin_class: str = "ECONOMY",
              currency: str = "INR", max_results: int = 5) -> list:
        date_str = departure_date.strftime("%Y-%m-%d")
        results  = []
        try:
            resp = self._client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=date_str,
                adults=adults,
                travelClass=cabin_class,
                currencyCode=currency,
                max=max_results,
                nonStop=False,
            )
            for offer in resp.data:
                price    = float(offer["price"]["grandTotal"])
                itin     = offer["itineraries"][0]
                segs     = itin["segments"]
                stops    = len(segs) - 1
                carrier  = segs[0]["carrierCode"]
                duration = itin["duration"]
                results.append({
                    "Airline":     carrier,
                    "Price_INR":   price,
                    "Stops":       stops,
                    "Flight_Type": "Direct" if stops == 0 else f"{stops}-Stop",
                    "Duration":    duration,
                })
        except self._ResponseError as error:
            code = getattr(error, "code", "")
            desc = getattr(error, "description", str(error))
            if "429" in str(code) or "rate" in str(desc).lower():
                log.warning(f"Rate limit hit ({origin}->{destination} {date_str}). Sleeping 30s...")
                time.sleep(30)
            elif "NO_OFFERS_FOUND" not in str(desc):
                log.debug(f"Amadeus [{code}]: {desc}")
        except Exception as exc:
            log.warning(f"Amadeus error ({origin}->{destination} {date_str}): {exc}")
        return results

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 7B - ASYNC PLAYWRIGHT FETCHER (Option B)
#
#  Uses playwright.async_api so it works correctly inside asyncio.gather().
#  playwright-stealth v2 apply_stealth_async() patches browser fingerprints.
#  For personal research only. Do NOT use commercially.
# ─────────────────────────────────────────────────────────────────────────────

class PlaywrightFlightFetcher:
    """
    Async Playwright scraper. Call fetch_async() from an asyncio context.
    Each instance owns its own browser — safe for concurrent use via asyncio.
    """

    def __init__(self):
        try:
            import playwright.async_api  # noqa: validate installed
        except ImportError:
            sys.exit("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
        try:
            from playwright_stealth import Stealth  # type: ignore
            self._Stealth = Stealth
        except ImportError:
            sys.exit("ERROR: playwright-stealth not found. Run: pip install playwright-stealth")

        self._pw      = None
        self._browser = None
        self._context = None
        self._page    = None

    async def _launch(self):
        from playwright.async_api import async_playwright
        self._pw      = await async_playwright().__aenter__()
        self._browser = await self._pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        self._context = await self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            viewport={"width": 1366, "height": 768},
        )
        self._page = await self._context.new_page()
        # playwright-stealth v2 async API
        await self._Stealth().apply_stealth_async(self._page)
        log.info("[worker] Async stealth Chromium launched")

    async def close_async(self):
        try:
            if self._browser:
                await self._browser.close()
            if self._pw:
                await self._pw.__aexit__(None, None, None)
        except Exception:
            pass
        self._pw = self._browser = self._context = self._page = None

    async def fetch_async(
        self,
        origin: str,
        destination: str,
        departure_date,
        adults: int = 1,
        cabin_class: str = "ECONOMY",
        currency: str = "INR",
        max_results: int = 5,
        sleep_range: tuple = (2.0, 4.0),
    ) -> list:
        """
        3-layer extraction strategy:
          Layer 1: aria-label attributes (stable - Google puts full flight
                   info like 'IndiGo, 2 hours 5 minutes, Nonstop, Rs5,299')
          Layer 2: role=listitem structural elements
          Layer 3: full page-text regex (ultimate fallback)
        """
        import asyncio, re

        if self._browser is None:
            await self._launch()

        date_str = departure_date.strftime("%Y-%m-%d")
        url = (
            f"https://www.google.com/travel/flights?q="
            f"flights+from+{origin}+to+{destination}+on+{date_str}"
            f"&curr=INR&hl=en-IN"
        )

        results = []
        try:
            await self._page.goto(url, timeout=30_000, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(*sleep_range))

            # Dismiss consent dialog
            for btn in ["Accept all", "Agree", "I agree", "Accept"]:
                try:
                    await self._page.click(f'button:has-text("{btn}")', timeout=2000)
                    await asyncio.sleep(1.0)
                    break
                except Exception:
                    pass

            # Wait for any meaningful content
            for sel in ["[aria-label]", '[role="listitem"]', "ul", "[data-id]"]:
                try:
                    await self._page.wait_for_selector(sel, timeout=8_000)
                    break
                except Exception:
                    continue
            await asyncio.sleep(2.0)

            # ── Layer 1: aria-label (most reliable) ──────────────────────────
            aria_els = await self._page.query_selector_all("[aria-label]")
            for el in aria_els:
                try:
                    label = await el.get_attribute("aria-label") or ""
                    ll    = label.lower()
                    # Google Flights aria-labels in India might say 'hr' or 'hour', and '₹' or 'rupee'
                    if not ("hour" in ll or "hr" in ll or "m" in ll):
                        continue
                    price = _extract_best_price(label)
                    if price <= 0:
                        continue
                    
                    stops    = 0 if "nonstop" in ll else (1 if "1 stop" in ll else 2)
                    
                    # Extract airline: it's usually at the beginning of the label or after "Flights with"
                    airline = "Unknown"
                    if "flights with" in ll:
                        m_air = re.search(r"with\s+([^.]+)", label, re.I)
                        if m_air: airline = m_air.group(1).strip()
                    else:
                        m_air = re.match(r"^([^,]+)", label)
                        if m_air: airline = m_air.group(1).strip()
                        
                    m_dur    = re.search(r"(\d+\s*hours?\s*(?:\d+\s*minutes?)?)", label, re.I)
                    duration = m_dur.group(1).strip()  if m_dur else "N/A"
                    
                    results.append({
                        "Airline":     airline[:35],
                        "Price_INR":   price,
                        "Stops":       stops,
                        "Flight_Type": "Direct" if stops == 0 else f"{stops}-Stop",
                        "Duration":    duration,
                    })
                    if len(results) >= max_results:
                        break
                except Exception:
                    continue

            # ── Layer 2: role=listitem ────────────────────────────────────────
            if not results:
                items = await self._page.query_selector_all('[role="listitem"]')
                for item in items[:20]:
                    try:
                        text  = await item.inner_text()
                        price = _extract_best_price(text)
                        if price <= 0:
                            continue
                        ll    = text.lower()
                        stops = 0 if "nonstop" in ll else (1 if "1 stop" in ll else 2)
                        results.append({
                            "Airline":     "Unknown",
                            "Price_INR":   price,
                            "Stops":       stops,
                            "Flight_Type": "Direct" if stops == 0 else f"{stops}-Stop",
                            "Duration":    "N/A",
                        })
                        if len(results) >= max_results:
                            break
                    except Exception:
                        continue

            # ── Layer 3: full-page text regex ─────────────────────────────────
            if not results:
                try:
                    body = await self._page.inner_text("body")
                    hits = re.findall(
                        r"[\u20b9]\s?([\d,]+)|INR\s?([\d,]+)|([\d,]+)\s*rupee",
                        body, re.I
                    )
                    seen_p: set = set()
                    for match in hits[:max_results * 3]:
                        raw   = next((m for m in match if m), "")
                        price = _extract_best_price(raw)
                        if price > 500 and price not in seen_p:
                            seen_p.add(price)
                            results.append({
                                "Airline":     "Unknown",
                                "Price_INR":   price,
                                "Stops":       0,
                                "Flight_Type": "Unknown",
                                "Duration":    "N/A",
                            })
                        if len(results) >= max_results:
                            break
                except Exception:
                    pass

            # De-duplicate and sort cheapest first
            if results:
                seen_set: set = set()
                deduped = []
                for r in sorted(results, key=lambda x: x["Price_INR"]):
                    if r["Price_INR"] not in seen_set:
                        seen_set.add(r["Price_INR"])
                        deduped.append(r)
                results = deduped[:max_results]

        except Exception as exc:
            log.warning(f"Scrape error ({origin}->{destination} {date_str}): {exc}")

        return results

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 8 - MAIN ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────

class FlightAnalyzerBot:
    """
    Orchestrates radius search, date sampling, and parallel flight fetching.
    Option B (Playwright) -> asyncio.Semaphore concurrency (no thread conflicts)
    Option A (Amadeus)   -> ThreadPoolExecutor (HTTP is thread-safe)
    """

    def __init__(self, config: dict):
        import threading
        self.cfg        = config
        self.radius     = RadiusSearchEngine(INDIAN_AIRPORTS)
        self.records    = []
        self._lock      = threading.Lock()
        self._source    = config["DATA_SOURCE"].upper()
        self._n_workers = max(1, config.get("PARALLEL_WORKERS", 3))
        log.info(
            f"Mode: {'Amadeus API' if self._source == 'A' else 'Playwright Async'} "
            f"| Workers: {self._n_workers}"
        )

    # ── Entry point ───────────────────────────────────────────────────────────
    def run(self):
        import asyncio

        log.info("=" * 68)
        log.info("  FLIGHT PRICE ANALYZER BOT - RADIUS SEARCH EDITION")
        log.info("=" * 68)

        dest_lat, dest_lon = self.radius.resolve_coordinates(self.cfg["TARGET_DESTINATION"])
        nearby = self.radius.find_airports_in_radius(dest_lat, dest_lon, self.cfg["RADIUS_KM"])

        if not nearby:
            log.error(f"No airports found within {self.cfg['RADIUS_KM']} km. Increase RADIUS_KM.")
            return

        log.info(f"\nAirports within {self.cfg['RADIUS_KM']} km of '{self.cfg['TARGET_DESTINATION']}':")
        log.info(f"  {'IATA':<6} {'Dist (km)':>10}  Name")
        log.info(f"  {'----':<6} {'---------':>10}  ----")
        for ap in nearby:
            log.info(f"  {ap['iata']:<6} {ap['dist_km']:>10.1f}  {ap['name']}")

        search_dates = generate_search_dates(
            interval_days=self.cfg["DATE_INTERVAL_DAYS"],
            window_days=60,
            include_weekends=self.cfg["INCLUDE_WEEKENDS"],
        )

        origin     = self.cfg["ORIGIN_AIRPORT"]
        work_items = [(ap, d) for ap in nearby for d in search_dates]
        total      = len(work_items)
        log.info(
            f"\nTotal queries: {total} "
            f"({len(nearby)} airports x {len(search_dates)} dates) "
            f"| Workers: {self._n_workers}\n"
        )

        if self._source == "B":
            # Playwright needs its own asyncio event loop
            asyncio.run(self._run_async_playwright(origin, work_items, total))
        else:
            # Amadeus HTTP calls are thread-safe
            self._run_threaded_amadeus(origin, work_items, total)

        self._export_results()

    # ── Option B: async Playwright ────────────────────────────────────────────
    async def _run_async_playwright(self, origin: str, work_items: list, total: int):
        import asyncio

        sem       = asyncio.Semaphore(self._n_workers)
        completed = [0]
        alock     = asyncio.Lock()

        log.info(f"[>>] Launching {self._n_workers} async Playwright workers ...")

        async def fetch_one(ap: dict, dep_date) -> tuple:
            fetcher = PlaywrightFlightFetcher()
            async with sem:
                try:
                    offers = await fetcher.fetch_async(
                        origin=origin,
                        destination=ap["iata"],
                        departure_date=dep_date,
                        adults=self.cfg["ADULTS"],
                        cabin_class=self.cfg["CABIN_CLASS"],
                        currency=self.cfg["CURRENCY"],
                        max_results=self.cfg["MAX_RESULTS_PER_QUERY"],
                        sleep_range=(self.cfg["SLEEP_MIN"], self.cfg["SLEEP_MAX"]),
                    )
                except Exception as e:
                    log.warning(f"  Worker error ({ap['iata']} {dep_date}): {e}")
                    offers = []
                finally:
                    await fetcher.close_async()
            return ap, dep_date, offers

        tasks = [fetch_one(ap, d) for ap, d in work_items]

        for coro in asyncio.as_completed(tasks):
            ap, dep_date, offers = await coro
            async with alock:
                completed[0] += 1
                done = completed[0]
                pct  = done / total * 100

            date_label = dep_date.strftime("%d %b %Y")
            if offers:
                best = min(o["Price_INR"] for o in offers)
                log.info(
                    f"  [{done:>3}/{total} {pct:4.0f}%] "
                    f"{origin}->{ap['iata']}  {date_label:<14} "
                    f"{len(offers):>2} offers  Rs{best:>8,.0f}"
                )
                with self._lock:
                    for offer in offers:
                        self.records.append(self._build_record(origin, ap, dep_date, offer))
            else:
                log.info(
                    f"  [{done:>3}/{total} {pct:4.0f}%] "
                    f"{origin}->{ap['iata']}  {date_label:<14} No flights"
                )

        log.info(f"\n[OK] All {total} async queries done. {len(self.records)} offers collected.")

    # ── Option A: threaded Amadeus ────────────────────────────────────────────
    def _run_threaded_amadeus(self, origin: str, work_items: list, total: int):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading

        completed = [0]
        lock      = threading.Lock()
        # Share one Amadeus client across threads (it's thread-safe)
        fetcher   = AmadeusFlightFetcher(
            api_key=self.cfg["AMADEUS_API_KEY"],
            api_secret=self.cfg["AMADEUS_API_SECRET"],
            hostname=self.cfg["AMADEUS_HOSTNAME"],
        )
        log.info(f"[>>] Launching {self._n_workers} Amadeus API workers ...")

        def do_fetch(ap: dict, dep_date) -> tuple:
            offers = fetcher.fetch(
                origin=origin,
                destination=ap["iata"],
                departure_date=dep_date,
                adults=self.cfg["ADULTS"],
                cabin_class=self.cfg["CABIN_CLASS"],
                currency=self.cfg["CURRENCY"],
                max_results=self.cfg["MAX_RESULTS_PER_QUERY"],
            )
            time.sleep(random.uniform(self.cfg["SLEEP_MIN"], self.cfg["SLEEP_MAX"]))
            return ap, dep_date, offers

        with ThreadPoolExecutor(max_workers=self._n_workers) as pool:
            futures = {pool.submit(do_fetch, ap, d): (ap, d) for ap, d in work_items}
            for future in as_completed(futures):
                try:
                    ap, dep_date, offers = future.result()
                except Exception as exc:
                    ap, dep_date = futures[future]
                    log.warning(f"  Thread error ({ap['iata']} {dep_date}): {exc}")
                    offers = []

                with lock:
                    completed[0] += 1
                    done = completed[0]
                    pct  = done / total * 100

                date_label = dep_date.strftime("%d %b %Y")
                if offers:
                    best = min(o["Price_INR"] for o in offers)
                    log.info(
                        f"  [{done:>3}/{total} {pct:4.0f}%] "
                        f"{origin}->{ap['iata']}  {date_label:<14} "
                        f"{len(offers):>2} offers  Rs{best:>8,.0f}"
                    )
                    with self._lock:
                        for offer in offers:
                            self.records.append(self._build_record(origin, ap, dep_date, offer))
                else:
                    log.info(
                        f"  [{done:>3}/{total} {pct:4.0f}%] "
                        f"{origin}->{ap['iata']}  {date_label:<14} No flights"
                    )

        log.info(f"[OK] All {total} queries done. {len(self.records)} offers collected.")

    def _build_record(self, origin: str, ap: dict, dep_date, offer: dict) -> dict:
        return {
            "Origin":            origin,
            "Destination_IATA":  ap["iata"],
            "Destination_Name":  ap["name"],
            "Destination_State": ap["state"],
            "Distance_km":       ap["dist_km"],
            "Date":              dep_date.strftime("%Y-%m-%d"),
            "Day_of_Week":       dep_date.strftime("%A"),
            "Airline":           offer["Airline"],
            "Price_INR":         offer["Price_INR"],
            "Flight_Type":       offer["Flight_Type"],
            "Stops":             offer.get("Stops", 0),
            "Duration":          offer.get("Duration", "N/A"),
            "Fetched_At":        datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # ── Analysis + Export ─────────────────────────────────────────────────────
    def _export_results(self):
        log.info("\n" + "=" * 68)
        log.info("  ANALYSIS AND EXPORT")
        log.info("=" * 68)

        if not self.records:
            log.warning("No flight data collected. Nothing to export.")
            return

        df = pd.DataFrame(self.records)
        df["Price_INR"] = pd.to_numeric(df["Price_INR"], errors="coerce")
        df.dropna(subset=["Price_INR"], inplace=True)
        df.sort_values("Price_INR", ascending=True, inplace=True, ignore_index=True)

        log.info(f"\nTotal results: {len(df)} offers")
        log.info("\nTOP 10 CHEAPEST FLIGHTS:")
        log.info(f"  {'#':<4} {'Date':<12} {'Origin':<6} {'Dest':<6} {'Airline':<20} {'Type':<8} {'Price (INR)':>14}")
        log.info(f"  {'-'*4} {'-'*12} {'-'*6} {'-'*6} {'-'*20} {'-'*8} {'-'*14}")
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            log.info(
                f"  {i+1:<4} {row['Date']:<12} {row['Origin']:<6} "
                f"{row['Destination_IATA']:<6} {str(row['Airline'])[:20]:<20} "
                f"{row['Flight_Type']:<8} Rs{row['Price_INR']:>12,.0f}"
            )

        log.info("\nCHEAPEST PER DESTINATION AIRPORT:")
        cheapest = (
            df.groupby(["Destination_IATA", "Destination_Name"])["Price_INR"]
            .agg(["min", "mean", "count"])
            .rename(columns={"min": "Min_Price", "mean": "Avg_Price", "count": "Offers"})
            .reset_index().sort_values("Min_Price")
        )
        for _, row in cheapest.iterrows():
            log.info(
                f"  {row['Destination_IATA']} | {row['Destination_Name'][:38]:<38} | "
                f"Rs{row['Min_Price']:>8,.0f}  (avg Rs{row['Avg_Price']:,.0f}, {row['Offers']:.0f} offers)"
            )

        df["Is_Weekend"] = df["Day_of_Week"].isin(["Friday", "Saturday", "Sunday"])
        w_avg = df[df["Is_Weekend"]]["Price_INR"].mean()
        d_avg = df[~df["Is_Weekend"]]["Price_INR"].mean()
        if not (pd.isna(w_avg) or pd.isna(d_avg)):
            cheaper = "WEEKENDS" if w_avg < d_avg else "WEEKDAYS"
            log.info(f"\nWeekend avg: Rs{w_avg:,.0f}  |  Weekday avg: Rs{d_avg:,.0f}  => {cheaper} are cheaper")

        out_dir = Path(self.cfg["OUTPUT_DIR"])
        out_dir.mkdir(parents=True, exist_ok=True)
        ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
        origin    = self.cfg["ORIGIN_AIRPORT"]
        dest_slug = self.cfg["TARGET_DESTINATION"].split(",")[0].strip().replace(" ", "_")
        stem      = f"flights_{origin}_to_{dest_slug}_{ts}"
        fmt       = self.cfg["OUTPUT_FORMAT"].lower()

        if fmt in ("csv", "both"):
            p = out_dir / f"{stem}.csv"
            df.to_csv(p, index=False, encoding="utf-8-sig")
            log.info(f"\nCSV saved  -> {p.resolve()}")

        if fmt in ("excel", "both"):
            p = out_dir / f"{stem}.xlsx"
            with pd.ExcelWriter(p, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="All Flights", index=False)
                cheapest.to_excel(writer, sheet_name="Cheapest by Airport", index=False)
                df.head(10).to_excel(writer, sheet_name="Top 10 Cheapest", index=False)
                for sheet in writer.sheets.values():
                    for col in sheet.columns:
                        try:
                            w = max(len(str(c.value)) for c in col if c.value is not None)
                            sheet.column_dimensions[col[0].column_letter].width = min(w + 3, 45)
                        except Exception:
                            pass
            log.info(f"Excel saved -> {p.resolve()}")

        log.info("\nDone! Happy travels!")

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 9 - ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if CONFIG["DATA_SOURCE"].upper() == "A" and "YOUR_AMADEUS" in CONFIG["AMADEUS_API_KEY"]:
        print("""
+----------------------------------------------------------+
|  WARNING: AMADEUS API KEY NOT SET                        |
|  1. Visit https://developers.amadeus.com/               |
|  2. Sign up (free) -> My Apps -> Create New App          |
|  3. Paste API Key & Secret into CONFIG at top of file    |
|  OR: Set DATA_SOURCE = 'B' to use Playwright scraper    |
+----------------------------------------------------------+
""")
        sys.exit(1)

    bot_config = CONFIG.copy()
    
    print("\n" + "="*60)
    print(" 🛫 FLIGHT PRICE ANALYZER BOT")
    print("="*60)
    
    # Ask for arrival location (target destination)
    user_dest = input(f"\nEnter arrival location [default: {CONFIG['TARGET_DESTINATION']}]: ").strip()
    if user_dest:
        bot_config["TARGET_DESTINATION"] = user_dest

    bot = FlightAnalyzerBot(bot_config)
    try:
        bot.run()
    except KeyboardInterrupt:
        log.info("\nInterrupted. Saving collected data...")
        bot._export_results()
    except Exception as fatal:
        log.error(f"Fatal error: {fatal}")
        log.debug(traceback.format_exc())
        sys.exit(1)
