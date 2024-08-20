from django.shortcuts import render, redirect
from .forms import PDFUploadForm
from .pdf_processing import extract_encounter_data
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os




def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pdf_file = request.FILES['pdf_file']
                pdf_path = f'media/{pdf_file.name}'
            
                with open(pdf_path, 'wb+') as destination:
                    for chunk in pdf_file.chunks():
                        destination.write(chunk)

                encounter_data = extract_encounter_data(pdf_path)
                request.session['encounter_data'] = encounter_data
               
                os.remove(pdf_path)

                return render(request, 'extractor/upload.html', {
                    'form': form,
                    'encounter_data': encounter_data
                })
            except ValidationError as e:
                error = str(e)
                return render(request, 'extractor/upload.html', {
                    'form': form,
                    'error': error
                })
    else:
        form = PDFUploadForm()
        encounter_data = [] 

    return render(request, 'extractor/upload.html', {
        'form': form,
        'encounter_data': encounter_data
    })


