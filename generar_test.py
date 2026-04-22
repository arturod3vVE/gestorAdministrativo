import openpyxl
from datetime import datetime

wb = openpyxl.Workbook()
sheet = wb.active
sheet.title = "Carga de Auditoría"

# 1. Definir Encabezados
headers = ["Unidad", "Fecha", "Concepto", "Monto"]
sheet.append(headers)

datos = [
    ("87", "15/12/2024", "Auditoría - Cuotas Atrasadas 2024", 150.00),
    ("113", "10/01/2025", "Fondo de Auxilio Vial", 25.50),
    ("151", "05/02/2025", "Reparación de Techo Sede", 40.00),
    ("109", "19/02/2025", "Mensualidad Administrativa", 60.00),
    ("23", "20/12/2024", "Multa Disciplinaria Auditoría", 10.00),
    ("52", "01/01/2025", "Cargo de Mensualidad de agua", 100.00),
]

for fila in datos:
    sheet.append(fila)

# Guardar el archivo
nombre_archivo = "test_auditoria_conductores.xlsx"
wb.save(nombre_archivo)

print(f"✅ Archivo '{nombre_archivo}' generado con éxito.")