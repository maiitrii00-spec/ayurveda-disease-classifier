"""
app.py
-------
Ayurveda Disease Classification System - Flask web application.

Working of the system (as per project spec):
  1. User opens the application            -> "/" route
  2. User enters symptoms                  -> index.html form
  3. System validates the input            -> matcher.validate_input()
  4. Database is searched for matching diseases -> matcher.find_matching_diseases()
  5. If found, disease details & treatment are displayed -> results.html
  6. If not found, an appropriate message is shown        -> results.html (no_match)

Also includes:
  - Admin CRUD (Record Maintenance) for managing the disease database
  - Patient search history log
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, get_connection
from matcher import validate_input, find_matching_diseases

app = Flask(__name__)
app.secret_key = "ayurveda-disease-classifier-secret-key"  # change in production


# ---------------------------------------------------------------------------
# Ensure DB exists / seeded on startup
# ---------------------------------------------------------------------------
init_db(reseed=False)


# ---------------------------------------------------------------------------
# Core user-facing flow
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Step 1 & 2: User opens the application and sees the symptom entry form."""
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    """
    Step 3-6: Validate input, search DB, show results or 'not found' message.
    """
    patient_name = request.form.get("patient_name", "").strip()
    symptom_text = request.form.get("symptoms", "").strip()

    # Step 3: Validate input
    is_valid, error = validate_input(symptom_text)
    if not is_valid:
        flash(error, "error")
        return redirect(url_for("index"))

    # Step 4: Search database for matching diseases
    matches = find_matching_diseases(symptom_text)

    # Log to patient history (Patient History concept)
    conn = get_connection()
    top_match_name = matches[0]["name"] if matches else None
    conn.execute(
        "INSERT INTO search_history (patient_name, symptoms_entered, matched_disease) VALUES (?,?,?)",
        (patient_name or "Anonymous", symptom_text, top_match_name),
    )
    conn.commit()
    conn.close()

    # Step 5 & 6: Display results or "not found" message
    return render_template(
        "results.html",
        matches=matches,
        symptom_text=symptom_text,
        patient_name=patient_name or "Anonymous",
    )


@app.route("/history")
def history():
    """View past consultations (Patient History)."""
    conn = get_connection()
    records = conn.execute(
        "SELECT * FROM search_history ORDER BY id DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return render_template("history.html", records=records)


# ---------------------------------------------------------------------------
# Admin: Record Maintenance (CRUD operations on the disease database)
# ---------------------------------------------------------------------------

@app.route("/admin")
def admin_list():
    conn = get_connection()
    diseases = conn.execute("SELECT * FROM diseases ORDER BY name").fetchall()
    conn.close()
    return render_template("admin_list.html", diseases=diseases)


@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if request.method == "POST":
        _save_disease_from_form(request.form)
        flash("Disease record added successfully.", "success")
        return redirect(url_for("admin_list"))
    return render_template("admin_form.html", disease=None)


@app.route("/admin/edit/<int:disease_id>", methods=["GET", "POST"])
def admin_edit(disease_id):
    conn = get_connection()
    disease = conn.execute("SELECT * FROM diseases WHERE id=?", (disease_id,)).fetchone()
    conn.close()

    if disease is None:
        flash("Disease record not found.", "error")
        return redirect(url_for("admin_list"))

    if request.method == "POST":
        _save_disease_from_form(request.form, disease_id=disease_id)
        flash("Disease record updated successfully.", "success")
        return redirect(url_for("admin_list"))

    return render_template("admin_form.html", disease=disease)


@app.route("/admin/delete/<int:disease_id>", methods=["POST"])
def admin_delete(disease_id):
    conn = get_connection()
    conn.execute("DELETE FROM diseases WHERE id=?", (disease_id,))
    conn.commit()
    conn.close()
    flash("Disease record deleted.", "success")
    return redirect(url_for("admin_list"))


def _save_disease_from_form(form, disease_id=None):
    fields = (
        form.get("name", "").strip(),
        form.get("sanskrit_name", "").strip(),
        form.get("dosha", "").strip(),
        form.get("symptoms", "").strip(),
        form.get("causes", "").strip(),
        form.get("herbs", "").strip(),
        form.get("treatment", "").strip(),
        form.get("diet_recommendation", "").strip(),
        form.get("lifestyle_recommendation", "").strip(),
    )
    conn = get_connection()
    if disease_id is None:
        conn.execute("""
            INSERT INTO diseases
            (name, sanskrit_name, dosha, symptoms, causes, herbs, treatment,
             diet_recommendation, lifestyle_recommendation)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, fields)
    else:
        conn.execute("""
            UPDATE diseases SET
                name=?, sanskrit_name=?, dosha=?, symptoms=?, causes=?, herbs=?,
                treatment=?, diet_recommendation=?, lifestyle_recommendation=?
            WHERE id=?
        """, fields + (disease_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    app.run(debug=True)
