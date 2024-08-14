from django.shortcuts import render
from .forms import PDFUploadForm
from .pdf_processing import extract_encounter_data

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            pdf_path = f'media/{pdf_file.name}'
            
            with open(pdf_path, 'wb+') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)
            
            encounter_data = extract_encounter_data(pdf_path)
            
            return render(request, 'extractor/upload.html', {
                'form': form,
                'encounter_data': encounter_data
            })
    else:
        form = PDFUploadForm()
    
    return render(request, 'extractor/upload.html', {
        'form': form
    })
