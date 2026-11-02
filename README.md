# 🌊 Boond — Smart Water Harvesting Assistant

<p align="center">
  <strong>Explore rainwater harvesting potential, local rainfall, and groundwater observations.</strong><br>
  Built for the <strong>Smart India Hackathon (SIH)</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Google Gemini">
</p>

Boond brings practical water-planning tools and public environmental data together in one web application. Use it to explore a basic harvesting assessment, estimated costs, historical rainfall, and the nearest available CGWB groundwater observation.

---

## 🚀 Key Features

### 🏠 Harvesting Feasibility
Enter a location, rooftop area, and open-space area to see a basic feasibility result. The current webpage uses a simple area rule; the separate `POST /api/feasibility` endpoint provides a Gemini-generated recommendation and is not yet connected to the page.

### 💰 Money Matters
Explore estimated installation costs and example government-scheme suggestions. The webpage currently uses sample values, while `POST /api/cost` is a separate Gemini-backed endpoint. Verify costs and scheme eligibility with official sources.

### 📏 Groundwater Depth
Look up a nearby Central Ground Water Board (CGWB) monitoring station using a state and district, city, or locality. Boond resolves the place, finds a station in that state, and shows its reported groundwater depth, station district, distance, and observation date.

> A station reading describes the monitoring station, not an individual household well. The latest available record can be old, so check the date shown with the result.

### ☔ Rain Check
Fetch recent historical rainfall for a location and estimate the water that could be collected from a roof. Rainfall is sourced from Open-Meteo's historical weather service and is model-based, rather than a nearby rain-gauge measurement.

### 🔐 Accounts
Signup and login use PostgreSQL-backed account routes. A reachable database must be configured in `.env`.

---

## 🧮 How the Rainwater Estimate Works

Boond estimates collectable rainwater using a simple formula:

```text
Rainfall (mm) × Roof area (m²) × Runoff coefficient = Estimated litres
```

One millimetre of rain over one square metre is one litre before collection losses. The current default runoff coefficient is `0.8`; real results vary with roof material and collection-system efficiency.

---

## 🏗️ System Architecture

```text
┌──────────────────────────────┐
│  Web frontend                │
│  HTML · CSS · JavaScript     │
└──────────────┬───────────────┘
               │ requests
               ▼
┌──────────────────────────────┐
│  FastAPI application         │
│  Serves pages and API routes │
└──────────────┬───────────────┘
               │
       ┌───────┼───────────┬──────────────┐
       ▼       ▼           ▼              ▼
    Gemini  Open-Meteo   CGWB data    PostgreSQL
    agents  rainfall    groundwater   accounts
```

## 📂 Project Structure

| Project path | What it does |
| --- | --- |
| `main.py` | Creates the FastAPI app, registers routes, and serves the frontend. |
| `routers/` | Defines feasibility, cost, groundwater, rainfall, and account endpoints. |
| `agents/` | Holds Gemini recommendation code and a LangChain rainfall tool. |
| `waterdata/rainfall.py` | Resolves a place and fetches historical rainfall from Open-Meteo. |
| `waterdata/groundwater.py` | Resolves a location and finds the nearest CGWB station observation. |
| `frontend sih/` | Contains the HTML, CSS, and JavaScript pages. |
| `database.py`, `models.py` | Configure database access and define account models. |
| `create_tables.py` | Creates missing database tables without deleting existing data. |

---

## 🛠️ Tech Stack

| Area | Technologies |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy |
| Frontend | HTML, CSS, JavaScript |
| Database | PostgreSQL |
| AI tools | LangChain, Google Gemini |
| Weather | Open-Meteo Historical Weather API |
| Groundwater | National Water Data Portal (CGWB) |
| Place lookup | Open-Meteo Geocoding, OpenStreetMap Nominatim fallback |

---

## ⚙️ Run Locally

### 1. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project directory:

```dotenv
DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DATABASE"
GEMINI_API_KEY="your-gemini-api-key"
SECRET_KEY="your-long-random-secret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Keep `.env` private. It is excluded by `.gitignore`. For local development with Railway, use the PostgreSQL service's public connection URL.

### 3. Create database tables

After configuring a reachable database, run:

```bash
./venv/bin/python create_tables.py
```

This creates missing tables and leaves existing tables and data intact.

### 4. Start Boond

```bash
uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) for the landing page. The feature list is at `/feature.html`; Groundwater Depth is at `/feature3.html`; Rain Check is at `/feature4.html`.

---

## 🔌 API Examples

### Groundwater Depth

```bash
curl -X POST http://127.0.0.1:8000/api/groundwater \
  -H "Content-Type: application/json" \
  -d '{"state":"Delhi","district":"Saket"}'
```

The response includes the nearest station, its district, distance, groundwater depth, observation date, and data source.

### Rain Check

```bash
curl -X POST http://127.0.0.1:8000/api/rainfall \
  -H "Content-Type: application/json" \
  -d '{"location":"Jaipur, India","roof_area_m2":100,"days":30}'
```

The response includes resolved place details, daily and total rainfall, data coverage, estimated harvestable litres, and source information.

---

## 📌 Current Scope

- The feature-list page includes English and Hindi controls; individual feature pages request a location where needed.
- The first four feature cards have pages. Feasibility and cost pages are frontend demonstrations; their Gemini-backed API endpoints are separate.
- Cards 5–7 are placeholders and are not implemented yet.
- Rainfall figures are model-based estimates. Groundwater figures are monitoring-station readings and may be from older records.

## 🔮 Future Enhancements

- Connect the feasibility and cost pages to their API endpoints.
- Add rainfall charts and longer-term comparisons.
- Compare groundwater observations over time and flag older records clearly.
- Build out the runoff, health-alert, and contractor features before presenting them as available.

---

<p align="center"><em>Built for the Smart India Hackathon.</em></p>
