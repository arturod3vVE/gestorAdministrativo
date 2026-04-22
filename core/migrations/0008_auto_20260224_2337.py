import uuid
from django.db import migrations

def gen_uuid(apps, schema_editor):
    Socio = apps.get_model('core', 'Socio')
    for socio in Socio.objects.all():
        socio.codigo_verificacion = uuid.uuid4()
        socio.save(update_fields=['codigo_verificacion'])

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_socio_codigo_verificacion_and_more'), # Asegúrate que apunte a la anterior
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]