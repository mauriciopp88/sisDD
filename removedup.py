import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisDD.settings')
django.setup()

from core.models import WorkRecord


def remove_duplicates():
    unique_records = set()
    duplicates = []

    for record in WorkRecord.objects.all():
        identifier = (record.employee_id, record.project_id, record.date)
        if identifier in unique_records:
            duplicates.append(record.id)
        else:
            unique_records.add(identifier)

    # Elimina registros duplicados
    if duplicates:
        WorkRecord.objects.filter(id__in=duplicates).delete()
        print(f"Eliminados {len(duplicates)} registros duplicados.")


if __name__ == "__main__":
    remove_duplicates()
