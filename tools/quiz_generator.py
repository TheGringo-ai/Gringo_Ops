

def generate_quiz(document_text: str):
    """
    Placeholder quiz generator that creates sample multiple choice questions
    from the uploaded document text. Real implementation would use an LLM.
    """
    if not document_text.strip():
        return []

    # Example hardcoded questions for testing
    return [
        {
            "question": "What is the purpose of a work order?",
            "options": ["To track tasks", "To monitor lunch breaks", "To assign lockers", "To grade quizzes"]
        },
        {
            "question": "Which tool is used for tightening bolts?",
            "options": ["Wrench", "Screwdriver", "Hammer", "Pliers"]
        }
    ]