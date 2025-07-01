from flask import Flask, jsonify
from . import database


app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Welcome to the ChatterFix API!"})

@app.route("/firestore-test")
def firestore_test():
    """An endpoint to explicitly test the Firestore connection."""
    try:
        # The get_db function will handle initialization on the first call
        db = database.get_db()
        doc_ref = db.collection("debug").document("ping")
        doc_ref.set({"status": "ok", "timestamp": "now"})
        # Verify the write
        doc = doc_ref.get()
        if doc.exists:
            return jsonify({"status": "success", "message": "Successfully connected to Firestore and performed a write/read operation. ✅"})
        else:
             return jsonify({"status": "error", "message": "Write operation seemed to succeed, but could not read the document back."}), 500

    except ConnectionError as ce:
        return jsonify({"status": "error", "message": f"Failed to connect to Firestore: {str(ce)}"}), 500
    except Exception as e:
        # Catch other potential exceptions from google-cloud-firestore
        return jsonify({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}), 500

# This allows running the app locally for testing
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
