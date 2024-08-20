import re
from pdfminer.high_level import extract_text
from django.core.exceptions import ValidationError
from .models import Disease

def extract_text_by_page(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            return extract_text(f).split("\f")
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return []


# def extract_encounter_data(pdf_path):
#     pages = extract_text_by_page(pdf_path)
#     encounter_data = []
    
#     encounter_pattern = re.compile(r'Encounter Date\s*:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3})', re.IGNORECASE)
#     diagnosis_heading_pattern = re.compile(r'Diagnosis', re.IGNORECASE)
#     bullet_point_pattern = re.compile(r'•\s*(.+)', re.IGNORECASE)
   
#     encounter_found = False
#     diagnosis_found = False
    
#     encounter_pages = []
#     for page_number, page_text in enumerate(pages, start=1):
#         encounters = encounter_pattern.findall(page_text)
#         if encounters:
#             encounter_found = True
#             for encounter in encounters:
#                 encounter_pages.append((page_number, encounter))
#         if diagnosis_heading_pattern.search(page_text):
#             diagnosis_found = True
           

   
#     if not encounter_found or not diagnosis_found:
#         raise ValidationError("The PDF does not contain the required keys: 'Encounter Date' or 'Diagnosis'.")

#     for page_number, encounter in encounter_pages:
        
#         diagnoses = []
#         for p in range(page_number - 1, len(pages)):
#             page_text = pages[p]
#             heading_match = diagnosis_heading_pattern.search(page_text)
#             if heading_match:
#                 heading_index = heading_match.end()
#                 relevant_text = page_text[heading_index:]
#                 bullet_points = bullet_point_pattern.findall(relevant_text)
#                 for bullet_point in bullet_points:
#                     diagnoses.append(bullet_point.strip())
#                 if diagnoses:
#                     break
        
#         encounter_data.append({
#             'Encounter_Date': encounter,
#             'Page': page_number,
#             'Diagnoses': diagnoses
#         })

#         print(encounter_data)
        

#     return encounter_data



def extract_encounter_data(pdf_path):
    
    pages = extract_text_by_page(pdf_path)
    encounter_data = []

    encounter_pattern = re.compile(r'Encounter Date\s*:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3})', re.IGNORECASE)
    diagnosis_heading_pattern = re.compile(r'Diagnosis', re.IGNORECASE)
    bullet_point_pattern = re.compile(r'•\s*(.+)', re.IGNORECASE)

    target_diseases = set(Disease.objects.values_list('name', flat=True))
    
    encounter_found = False
    diagnosis_found = False

    encounter_pages = []
    for page_number, page_text in enumerate(pages, start=1):
        encounters = encounter_pattern.findall(page_text)
        if encounters:
            encounter_found = True
            for encounter in encounters:
                encounter_pages.append((page_number, encounter))
        
        if diagnosis_heading_pattern.search(page_text):
            diagnosis_found = True

    if not encounter_found or not diagnosis_found:
        raise ValidationError("The PDF does not contain the required keys: 'Encounter Date' or 'Diagnosis'.")

    for page_number, encounter in encounter_pages:
        diagnoses = []
        for p in range(page_number - 1, len(pages)):
            page_text = pages[p]
            heading_match = diagnosis_heading_pattern.search(page_text)
            if heading_match:
                heading_index = heading_match.end()
                relevant_text = page_text[heading_index:]
                bullet_points = bullet_point_pattern.findall(relevant_text)
                
                for bullet_point in bullet_points:
                    disease_name = bullet_point.strip()
                    
                    try:
                      
                        if disease_name in target_diseases:
                            disease = Disease.objects.get(name=disease_name)
                            diagnoses.append({
                                'name': disease_name,
                                'code': disease.code
                            })
                    except Disease.DoesNotExist:
                       
                        diagnoses.append({
                            'name': disease_name,
                            'code': 'Not found'
                        })
                break 
        
        
        if diagnoses:
            encounter_data.append({
                'EncounterDate': encounter,
                'Page': page_number,
                'Diagnoses': diagnoses
            })
    
    return encounter_data