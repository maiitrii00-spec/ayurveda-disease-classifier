"""
database.py
------------
Handles all database creation, seeding, and low-level data access
for the Ayurveda Disease Classification System.

Tables:
    diseases        -> the core digital database of Ayurvedic diseases
    search_history   -> patient/consultation history (Patient History concept)
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ayurveda.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(reseed=False):
    """Create tables. If reseed=True, drop and reseed with sample data."""
    conn = get_connection()
    cur = conn.cursor()

    if reseed:
        cur.execute("DROP TABLE IF EXISTS diseases")
        cur.execute("DROP TABLE IF EXISTS search_history")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sanskrit_name TEXT,
            dosha TEXT NOT NULL,               -- Vata / Pitta / Kapha / combination
            symptoms TEXT NOT NULL,            -- comma separated keywords
            causes TEXT,
            herbs TEXT,                        -- comma separated herb names
            treatment TEXT,
            diet_recommendation TEXT,
            lifestyle_recommendation TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            symptoms_entered TEXT NOT NULL,
            matched_disease TEXT,
            searched_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) AS c FROM diseases")
    count = cur.fetchone()["c"]

    if reseed or count == 0:
        seed_diseases(conn)

    conn.close()


def seed_diseases(conn):
    diseases = [
        (
            "Amlapitta (Hyperacidity)", "Amlapitta", "Pitta",
            "heartburn,acidity,sour belching,nausea,burning sensation in chest,indigestion,vomiting",
            "Excessive intake of spicy/oily/fried food, irregular eating habits, stress, alcohol",
            "Amalaki,Yashtimadhu,Shatavari,Guduchi",
            "Avipattikar Churna and Yashtimadhu are commonly used to pacify aggravated Pitta and reduce acid formation.",
            "Avoid spicy, sour and fried foods. Prefer cooling foods like milk, ghee, coconut water and sweet fruits.",
            "Avoid daytime sleeping, eat on time, avoid stress and late-night meals."
        ),
        (
            "Jwara (Fever)", "Jwara", "Tridosha (Vata-Pitta-Kapha)",
            "high temperature,body ache,chills,headache,fatigue,loss of appetite,sweating",
            "Ama (toxin) accumulation, seasonal change, infection, weakened Agni (digestive fire)",
            "Tulsi,Ginger,Guduchi,Sudarshan Ghan Vati",
            "Langhana (fasting therapy) followed by light diet; Guduchi and Sudarshan Churna help reduce fever.",
            "Light, warm, easily digestible food such as rice gruel (Peya). Avoid heavy and cold foods.",
            "Complete rest, avoid cold exposure, stay hydrated with warm water."
        ),
        (
            "Kasa (Cough)", "Kasa", "Vata-Kapha",
            "cough,throat irritation,phlegm,chest congestion,breathlessness,hoarse voice",
            "Dust, cold exposure, smoking, weak digestion producing Ama that affects lungs",
            "Tulsi,Vasaka,Pippali,Mulethi",
            "Sitopaladi Churna and Vasavaleha are commonly given to relieve cough and clear congestion.",
            "Warm fluids, avoid cold drinks, dairy, and fried food during active cough.",
            "Steam inhalation, avoid cold wind exposure, gargle with warm salt water."
        ),
        (
            "Shwasa (Asthma/Breathing Difficulty)", "Shwasa", "Vata-Kapha",
            "breathlessness,wheezing,chest tightness,difficulty breathing,cough,fatigue",
            "Excess Kapha blocking respiratory channels, cold and damp environment, allergies",
            "Vasaka,Pushkarmoola,Kantakari,Sitopaladi Churna",
            "Shwasa Kuthar Rasa and steam inhalation with therapeutic herbs help open airways.",
            "Avoid cold, heavy and mucus-forming foods like dairy and bananas. Prefer warm, light meals.",
            "Practice Pranayama (breathing exercises), avoid dust and smoke exposure."
        ),
        (
            "Atisara (Diarrhea)", "Atisara", "Vata-Pitta",
            "loose motion,frequent bowel movements,abdominal cramps,dehydration,weakness",
            "Contaminated food/water, excessive cold or spicy food, weak digestive fire",
            "Bilva,Musta,Kutaja,Jatiphala",
            "Kutajarishta and Bilva churna are traditionally used to control loose motions and restore Agni.",
            "Rice gruel, buttermilk, banana. Avoid oily, spicy and raw foods.",
            "Stay hydrated with ORS or coconut water, take adequate rest."
        ),
        (
            "Arsha (Piles/Hemorrhoids)", "Arsha", "Vata-Kapha",
            "rectal bleeding,pain during defecation,itching near anus,constipation,swelling",
            "Chronic constipation, sedentary lifestyle, spicy food, straining during bowel movement",
            "Triphala,Nagakesara,Haritaki",
            "Abhayarishta and Triphala Churna help regulate bowel movement and shrink hemorrhoidal swelling.",
            "High fiber diet with green leafy vegetables, whole grains, and plenty of water.",
            "Avoid prolonged sitting, practice regular light exercise, avoid straining during defecation."
        ),
        (
            "Prameha (Diabetes)", "Prameha", "Kapha (with Vata/Pitta variants)",
            "excessive thirst,frequent urination,fatigue,weight loss,blurred vision,slow healing wounds",
            "Sedentary lifestyle, excess sweet/heavy food intake, genetic predisposition, obesity",
            "Gudmar,Jamun seed,Neem,Karela,Methi",
            "Vasant Kusumakar Ras and Chandraprabha Vati are often used along with herbs like Gudmar to manage blood sugar.",
            "Low glycemic, high fiber diet. Avoid sweets, refined sugar and excess rice/potato.",
            "Regular exercise, weight management, routine blood sugar monitoring."
        ),
        (
            "Kushtha (Skin Disorders)", "Kushtha", "Tridosha (Kapha-Pitta dominant)",
            "itching,skin rash,redness,scaling,discoloration of skin,dryness,eruptions",
            "Blood impurities, incompatible food combinations, poor digestion, stress",
            "Neem,Manjistha,Khadira,Haridra (Turmeric)",
            "Panchakarma detox (especially Raktamokshana) along with Neem and Manjistha helps purify blood and skin.",
            "Avoid incompatible food combinations (e.g., milk with fish), reduce sour and fried foods.",
            "Maintain skin hygiene, avoid excessive sun exposure, manage stress."
        ),
        (
            "Sandhivata (Osteoarthritis/Joint Pain)", "Sandhivata", "Vata",
            "joint pain,stiffness,swelling in joints,reduced mobility,cracking sound in joints",
            "Aging, excess Vata aggravation, sedentary lifestyle, cold weather exposure",
            "Guggulu,Ashwagandha,Shallaki,Rasna",
            "Mahanarayan Taila for external massage and Yograj Guggulu internally help reduce joint pain and stiffness.",
            "Warm, unctuous (oily) foods. Avoid cold, dry and raw foods. Include ghee in diet.",
            "Gentle regular exercise, warm oil massage (Abhyanga), keep joints warm."
        ),
        (
            "Shirahshoola (Headache/Migraine)", "Shirahshoola", "Vata-Pitta",
            "headache,throbbing pain,sensitivity to light,nausea,eye strain,dizziness",
            "Stress, irregular sleep, dehydration, excess sun/heat exposure, eye strain",
            "Brahmi,Jatamansi,Shankhpushpi",
            "Shirodhara therapy with medicated oils and Brahmi Vati help calm the nervous system and relieve pain.",
            "Regular meals, avoid skipping meals, stay hydrated, avoid excess caffeine.",
            "Adequate sleep, stress management, avoid prolonged screen exposure."
        ),
        (
            "Vibandha (Constipation)", "Vibandha", "Vata",
            "difficulty passing stool,hard stool,bloating,infrequent bowel movement,abdominal discomfort",
            "Low fiber diet, dehydration, irregular routine, excess Vata aggravation",
            "Triphala,Haritaki,Isabgol",
            "Triphala Churna taken at night with warm water is a classic remedy to regulate bowel movement.",
            "High fiber diet, warm water, fruits like papaya and figs.",
            "Regular physical activity, fixed meal and sleep times, avoid excessive dry/processed food."
        ),
        (
            "Grahani (Irritable Bowel Syndrome)", "Grahani", "Vata-Kapha",
            "irregular bowel movement,bloating,abdominal pain,alternating diarrhea and constipation,gas",
            "Weak digestive fire (Agni), irregular eating habits, stress, food intolerance",
            "Bilva,Musta,Chitrakadi Vati",
            "Chitrakadi Vati and dietary regulation are used to strengthen Agni and stabilize bowel function.",
            "Light, warm, freshly cooked meals at regular intervals. Avoid raw salads and cold food.",
            "Eat mindfully at fixed times, manage stress through yoga and meditation."
        ),
        (
            "Vatarakta (Gout)", "Vatarakta", "Vata-Rakta (blood)",
            "joint swelling,redness,burning pain in joints,tenderness,restricted movement",
            "Excess intake of red meat/sour/salty food, sedentary life, blood impurity",
            "Guduchi,Guggulu,Punarnava",
            "Punarnavadi Guggulu and blood-purifying herbs like Guduchi are used to reduce swelling and pain.",
            "Avoid red meat, sour and fermented foods. Include bitter vegetables and pomegranate.",
            "Adequate hydration, avoid prolonged standing, gentle joint mobility exercises."
        ),
        (
            "Unmada (Mental/Anxiety Disorders)", "Unmada", "Vata-Pitta (affecting mind)",
            "anxiety,restlessness,insomnia,mood swings,irritability,poor concentration",
            "Chronic stress, improper diet, disturbed sleep, genetic factors",
            "Brahmi,Ashwagandha,Jatamansi,Shankhpushpi",
            "Saraswatarishta and Brahmi-based formulations are used to calm the mind and improve mental clarity.",
            "Sattvic diet with fresh fruits, vegetables and warm milk. Avoid caffeine and processed food.",
            "Meditation, Pranayama, regular sleep schedule, reduce screen time before bed."
        ),
        (
            "Pinasa (Sinusitis/Allergic Rhinitis)", "Pinasa", "Kapha-Vata",
            "nasal congestion,runny nose,sneezing,facial pain,headache,reduced sense of smell",
            "Cold/damp weather, dust allergy, weak immunity, excess Kapha in sinuses",
            "Sitopaladi Churna,Tulsi,Pippali,Trikatu",
            "Nasya therapy (nasal instillation of medicated oil) along with Sitopaladi Churna helps clear sinuses.",
            "Warm, light food. Avoid cold, dairy and mucus-forming foods.",
            "Steam inhalation, avoid dust/pollen exposure, keep head and ears covered in cold weather."
        ),
    ]

    conn.executemany("""
        INSERT INTO diseases
        (name, sanskrit_name, dosha, symptoms, causes, herbs, treatment,
         diet_recommendation, lifestyle_recommendation)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, diseases)
    conn.commit()


if __name__ == "__main__":
    init_db(reseed=True)
    print("Database initialized and seeded at:", DB_PATH)
