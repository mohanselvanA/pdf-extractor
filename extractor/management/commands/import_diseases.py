import pandas as pd
from django.core.management.base import BaseCommand
from ...models import Disease  # Replace with your actual model import

class Command(BaseCommand):
    help = "Import disease data from an Excel file into the Disease model"

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file containing disease data')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        
        try:
            df = pd.read_excel(excel_file)
            self.stdout.write(self.style.SUCCESS(f'Successfully read {excel_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading {excel_file}: {e}'))
            return
        df.columns = df.columns.str.strip()
        
        if 'diseases' not in df.columns or 'code' not in df.columns:
            self.stdout.write(self.style.ERROR('Excel file must contain "diseases" and "code" columns'))
            return
        
        for index, row in df.iterrows():
            name = str(row['diseases']).strip()
            code = str(row['code']).strip()
            try:
                Disease.objects.update_or_create(name=name, defaults={'code': code})
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating/creating disease {name}: {e}'))
                continue

        self.stdout.write(self.style.SUCCESS('Successfully imported disease data'))
