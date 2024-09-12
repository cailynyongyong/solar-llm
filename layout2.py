import requests
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
 
api_key = os.getenv("UPSTAGE_API_KEY")
filename = "test.pdf"
 
url = "https://api.upstage.ai/v1/document-ai/layout-analysis"
headers = {"Authorization": f"Bearer {api_key}"}
files = {"document": open(filename, "rb")}
data = {"ocr": True}
response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())

layout_result = response.json()

# # Function to process layout elements
# def process_layout_elements(layout_result):
#     elements = []
#     for elem in layout_result['elements']:
#         bounding_box = elem['bounding_box']
#         font_size = int(elem['html'].split('font-size:')[1].split('px')[0])
#         text = elem['text'].replace("\n", "<br/>")
#         elements.append({
#             "id": elem['id'],
#             "x": bounding_box[0]['x'],
#             "y": bounding_box[0]['y'],
#             "width": bounding_box[1]['x'] - bounding_box[0]['x'],
#             "height": bounding_box[2]['y'] - bounding_box[0]['y'],
#             "font_size": font_size,
#             "text": text
#         })
#     return elements

# # Process the elements
# elements = process_layout_elements(layout_result)

# # Function to create PDF
# def create_pdf(file_path, elements, page_height):
#     c = canvas.Canvas(file_path, pagesize=letter)
#     width, height = letter
    
#     for element in elements:
#         x = element['x']
#         y = page_height - element['y']  # Flip y-axis for PDF coordinate system
#         text = element['text']
        
#         c.setFont("Helvetica", element['font_size'])
#         c.drawString(x, y, text)
    
#     c.save()

# # Get the page height from metadata
# page_height = layout_result['metadata']['pages'][0]['height']

# # Create the PDF
# create_pdf("output_invoice.pdf", elements, page_height)

import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Frame, Spacer
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Create a PDF document with bounding box information
def create_pdf(data, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create a canvas for custom positioning
    c = canvas.Canvas(filename, pagesize=letter)
    
    width, height = letter

    for element in data['elements']:
        x = element['bounding_box'][0]['x']
        y = height - element['bounding_box'][0]['y']  # Invert the y-axis for PDF coordinates
        w = element['bounding_box'][1]['x'] - element['bounding_box'][0]['x']
        h = element['bounding_box'][2]['y'] - element['bounding_box'][0]['y']
        
        if element['category'] == 'paragraph':
            text = element['text']
            p = Paragraph(text, styles['Normal'])
            f = Frame(x, y - h, w, h, showBoundary=0)
            f.addFromList([p], c)
        elif element['category'] == 'heading1':
            text = element['text']
            p = Paragraph(text, styles['Title'])
            f = Frame(x, y - h, w, h, showBoundary=0)
            f.addFromList([p], c)
        elif element['category'] == 'table':
            table_data = [row.split() for row in element['text'].split('\n')]
            table = Table(table_data, colWidths=w/len(table_data[0]))
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            f = Frame(x, y - h, w, h, showBoundary=0)
            f.addFromList([table], c)
    
    c.save()

# Example usage with the provided JSON data
create_pdf(layout_result, "output2.pdf")
