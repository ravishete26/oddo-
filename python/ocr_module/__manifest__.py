{
    'name': 'OCR Documents',
    'version': '1.0',
    'summary': 'Extract text from images and PDFs using Tesseract OCR',
    'category': 'Tools',
    'author': 'You',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ocr_document_views.xml',
    ],
    'installable': True,
    'application': True,
}
