import base64
import io
from odoo import models, fields
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

# On Windows, if needed, uncomment and set path to tesseract.exe:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class OcrDocument(models.Model):
    _name = 'ocr.document'
    _description = 'OCR Document'

    name = fields.Char(string='Title', required=True, default='New')
    file = fields.Binary(string='File', attachment=True)
    filename = fields.Char(string='Filename')
    language = fields.Char(string='Language', default='eng')
    extracted_text = fields.Text(string='Extracted Text', readonly=True)
    state = fields.Selection([('new','New'), ('done','Done'), ('error','Error')], default='new')

    def action_run_ocr(self):
        for rec in self:
            if not rec.file:
                rec.state = 'error'
                rec.extracted_text = 'No file uploaded.'
                continue
            try:
                file_bytes = base64.b64decode(rec.file)
                text = ''
                if rec.filename and rec.filename.lower().endswith('.pdf'):
                    # If on Windows and poppler isn't in PATH, add poppler_path argument:
                    # images = convert_from_bytes(file_bytes, poppler_path=r"C:\path\to\poppler\bin")
                    images = convert_from_bytes(file_bytes)
                    for img in images:
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        text += pytesseract.image_to_string(img, lang=rec.language or 'eng')
                else:
                    image = Image.open(io.BytesIO(file_bytes))
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    text = pytesseract.image_to_string(image, lang=rec.language or 'eng')

                rec.extracted_text = text
                rec.state = 'done'
            except Exception as e:
                rec.extracted_text = "OCR error: %s" % (e,)
                rec.state = 'error'
