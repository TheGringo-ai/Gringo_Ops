

def translate_text(text: str, lang: str) -> str:
    """
    Simple placeholder translation function.
    Real implementation should use Google Translate API or similar.
    """
    translations = {
        "Spanish": {
            "Technician Name": "Nombre del técnico",
            "Department": "Departamento",
            "Assigned Equipment": "Equipo asignado",
            "Upload a source document": "Subir un documento fuente",
            "Document uploaded successfully.": "Documento subido con éxito.",
            "Generate Quiz": "Generar cuestionario",
            "Please upload a document to generate a quiz.": "Por favor, sube un documento para generar un cuestionario.",
            "Export Training PDF": "Exportar PDF de entrenamiento",
            "Download Training PDF": "Descargar PDF de entrenamiento",
            "Log Training Completion": "Registrar finalización del entrenamiento",
            "Training logged successfully.": "Entrenamiento registrado con éxito.",
            "Technician name and training document required.": "Se requiere el nombre del técnico y el documento de entrenamiento."
        }
    }
    if lang == "Spanish" and text in translations["Spanish"]:
        return translations["Spanish"][text]
    return text