import re
from django.core.exceptions import ValidationError
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from .models import Disease

def extract_diagnosis_pdfminer(page_text, diagnosis_heading, next_heading, bullet_points):
    past_medical_history_text = []
    lines = page_text.split('\n')
    found_heading_on_page = False

    for line in lines:
        if diagnosis_heading.search(line) and not found_heading_on_page:
            found_heading_on_page = True
            continue
        elif next_heading.search(line):
            found_heading_on_page = False
            break
        elif found_heading_on_page:
            match = bullet_points.match(line)
            if match:
                past_medical_history_text.append(match.group(1))
    
    return past_medical_history_text

def extract_encounter_data(pdf_path):
    pages = extract_text(pdf_path, laparams=LAParams()).split('\f')
    encounter_data = []

    encounter_pattern = re.compile(r'Encounter Date\s*:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3})', re.IGNORECASE)
    diagnosis_heading = re.compile(r'Patient\s+Active\s+Problem\s+List', re.IGNORECASE)
    bullet_points = re.compile(r'•\s*(.+)', re.IGNORECASE)
    next_heading = re.compile(r'(Past Medical History:)', re.IGNORECASE)

    target_diseases = set(Disease.objects.values_list('name', flat=True))
    encounter_pages = []
    all_encounter_data = []
    seen_encounters = set()

    for page_number, page_text in enumerate(pages, start=1):
        encounters = encounter_pattern.findall(page_text)
        if encounters:
            for encounter in encounters:
                encounter_pages.append((page_number, encounter))

    for page_number, encounter in encounter_pages:
        if (encounter, page_number) in seen_encounters:
            continue
        diagnoses = []
        found_diagnosis = False

        for p in range(page_number - 1, len(pages)):
            page_text = pages[p]
            
            page_diagnoses = extract_diagnosis_pdfminer(page_text, diagnosis_heading, next_heading, bullet_points)
            
            if page_diagnoses:
               
                for diagnosis_text in page_diagnoses:
                    diagnosis_text = diagnosis_text.strip()
                    if diagnosis_text:
                        if diagnosis_text in target_diseases:
                            try:
                                disease = Disease.objects.get(name__iexact=diagnosis_text)
                                diagnoses.append({
                                    'name': diagnosis_text,
                                    'code': disease.code
                                })
                            except Disease.DoesNotExist:
                                diagnoses.append({
                                    'name': diagnosis_text,
                                    'code': 'Not found'
                                })
                        else:
                            diagnoses.append({
                                'name': diagnosis_text,
                                'code': 'Not found'
                            })

            if p != page_number - 1 and (encounter_pattern.search(page_text) or next_heading.search(page_text)):
                break

        if page_diagnoses:
            all_encounter_data.append({
                'EncounterDate': encounter,
                'Page': page_number,
                'Diagnoses': diagnoses
            })
            seen_encounters.add((encounter, page_number))

    all_encounter_data = [entry for entry in all_encounter_data if entry['Diagnoses']]

    return all_encounter_data
