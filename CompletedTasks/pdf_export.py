# This file is used for exporting data to a PDF file

import pdfkit

def export_to_pdf(data, filename):
    """
    Export data to a PDF file

    Parameters:
    data (str): The data to be exported
    filename (str): The name of the PDF file

    Returns:
    None
    """
    try:
        pdfkit.from_string(data, filename)
        print(f"Data successfully exported to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Test the export_to_pdf function
data = "This is a sample data to be exported to a PDF file"
filename = "sample.pdf"
export_to_pdf(data, filename)

# Task: Add error handling for invalid filename inputs. Check if the filename contains any invalid characters.