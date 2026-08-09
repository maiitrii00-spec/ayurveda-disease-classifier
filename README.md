# 🌿 Ayurveda Disease Classification System

A web-based system that lets a user enter symptoms and searches a digital
Ayurvedic knowledge base to identify likely diseases, their dosha imbalance
(Vata / Pitta / Kapha), causes, recommended herbs, treatment, and diet &
lifestyle guidance.

Built with **Python (Flask)** + **SQLite**, no external services required.

> ⚠️ Educational project only — not a substitute for professional medical
> or Ayurvedic consultation.

## Features

- Symptom-based disease search using a keyword-overlap matching algorithm
- Digital database of 15 common Ayurvedic diseases (name, Sanskrit name,
  dosha, symptoms, causes, herbs, treatment, diet & lifestyle advice)
- Input validation before search
- "No match found" handling when no disease fits the entered symptoms
- Patient consultation history log
- Admin panel with full CRUD (Create, Read, Update, Delete) for managing
  disease records

## Working of the System

1. User opens the application
2. User enters symptoms
3. System validates the input
4. Database is searched for matching diseases
5. If found, disease details and treatment are displayed
6. If not found, an appropriate message is shown

## Project Structure

```
ayurveda-disease-classifier/
├── app.py                 # Flask application & routes
├── database.py             # DB schema creation + seed data (15 diseases)
├── matcher.py               # Symptom validation + search/classification algorithm
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html          # Symptom entry form
│   ├── results.html         # Matching diseases / not-found message
│   ├── history.html         # Patient consultation history
│   ├── admin_list.html       # Admin: list all diseases
│   └── admin_form.html       # Admin: add/edit disease
└── static/css/style.css
```

## Setup & Run

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ayurveda-disease-classifier

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python3 app.py
```

Then open **http://127.0.0.1:5000** in your browser.

The SQLite database (`ayurveda.db`) is created and seeded automatically
on first run — no manual setup needed.

To reset the database to the original seed data at any time:

```bash
python3 database.py
```

## How the Matching Algorithm Works (`matcher.py`)

1. The user's symptom text is normalized (lowercased, split on commas/`and`).
2. Each disease record's comma-separated `symptoms` field is compared
   against the user's tokens using substring overlap.
3. A match score (% of the disease's symptoms present in the user's input)
   is computed for every disease.
4. Diseases scoring above a threshold (25%) are returned, ranked by score.
5. If no disease clears the threshold, the system reports "no match found".

You can tune matching sensitivity via `MATCH_THRESHOLD` in `matcher.py`.

## Extending the Project

- Swap SQLite for PostgreSQL/MySQL for multi-user deployment
- Add user authentication for the admin panel
- Add a `patients` table to store body constitution (Prakriti) profiles
- Plug in an ML/NLP model for smarter symptom-to-disease prediction
- Deploy to Render/Railway/PythonAnywhere for a live demo link

## Conceptual Mapping (Ayurveda / IKS → Computer Science)

| Ayurveda / IKS Concept | CS Concept | Where in this project |
|---|---|---|
| Disease | Data Record | `diseases` table row |
| Patient | User | Person filling the symptom form |
| Symptoms | Input Data | `symptoms` textarea in `index.html` |
| Dosha (Vata/Pitta/Kapha) | Classification Category | `dosha` column, shown as a tag |
| Diagnosis | Algorithm | `matcher.find_matching_diseases()` |
| Ayurvedic Books | Database | `diseases` table (seeded from classical references) |
| Herbal Medicines | Database Records | `herbs` column |
| Treatment | Output | `results.html` treatment section |
| Disease Classification | Data Classification | Dosha tagging + match scoring |
| Ayurvedic Practitioner | Expert System | Rule-based scoring in `matcher.py` |
| Patient History | Database Table | `search_history` table |
| Consultation | User Interaction | Forms & navigation |
| Decision Making | Conditional Statements | `if`/`else` validation & routing logic in `app.py` |
| Disease Search | Searching Algorithm | Keyword overlap search in `matcher.py` |
| Record Maintenance | CRUD Operations | `/admin` routes |
| Multiple Diseases | Data Structure | List of `dict` rows returned from SQLite |

## License

MIT License — free to use and modify for academic/educational purposes.
