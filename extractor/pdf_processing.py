import re
from pdfminer.high_level import extract_text

def extract_text_by_page(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            return extract_text(f).split("\f")
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return []

def extract_encounter_data(pdf_path):
    pages = extract_text_by_page(pdf_path)
    encounter_data = []
    
    encounter_pattern = re.compile(r'Encounter Date\s*:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3})', re.IGNORECASE)
    diagnosis_heading_pattern = re.compile(r'Diagnosis', re.IGNORECASE)
    bullet_point_pattern = re.compile(r'•\s*(.+)', re.IGNORECASE)
    
    encounter_pages = []
    for page_number, page_text in enumerate(pages, start=1):
        encounters = encounter_pattern.findall(page_text)
        if encounters:
            for encounter in encounters:
                encounter_pages.append((page_number, encounter))

    for page_number, encounter in encounter_pages:
        diagnoses = []
        for p in range(page_number - 1, len(pages)):
            page_text = pages[p]
            heading_match = diagnosis_heading_pattern.search(page_text)
            if heading_match:
                heading_index = heading_match.end()
                relevant_text = page_text[heading_index:]
                next_heading_index = diagnosis_heading_pattern.search(relevant_text)
                if next_heading_index:
                    relevant_text = relevant_text[:next_heading_index.start()]
                bullet_points = bullet_point_pattern.findall(relevant_text)
                for bullet_point in bullet_points:
                    diagnoses.append(bullet_point.strip())
                if diagnoses:
                    break
        encounter_data.append({
            'encounter_date': encounter, 
            'page': page_number,           
            'diagnoses': diagnoses        
        })

    return encounter_data
