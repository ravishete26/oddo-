import base64
import io
from odoo import models, fields, api
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

class OcrDocument(models.Model):
    _name = 'ocr.document'
    _description = 'OCR Document'

    name = fields.Char(required=True, default='New')
    file = fields.Binary(string='File', attachment=True)
    filename = fields.Char()
    language = fields.Char(default='eng')
    state = fields.Selection([('new','New'), ('done','Done'), ('error','Error')], default='new')
    line_ids = fields.One2many('ocr.document.line', 'document_id', string='Extracted Lines')

    def action_run_ocr(self):
        for rec in self:
            if not rec.file:
                rec.state = 'error'
                continue
            try:
                file_bytes = base64.b64decode(rec.file)
                text = ''

                if rec.filename and rec.filename.lower().endswith('.pdf'):
                    images = convert_from_bytes(file_bytes)
                    for img in images:
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        text += pytesseract.image_to_string(img, lang=rec.language or 'eng', config='--psm 6')
                else:
                    image = Image.open(io.BytesIO(file_bytes))
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    text = pytesseract.image_to_string(image, lang=rec.language or 'eng', config='--psm 6')

                # Clear old lines
                rec.line_ids.unlink()

                # Split text into lines and store in child table
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                for idx, line_text in enumerate(lines, start=1):
                    self.env['ocr.document.line'].create({
                        'document_id': rec.id,
                        'sequence': idx,
                        'content': line_text,
                    })

                rec.state = 'done'
            except Exception as e:
                rec.state = 'error'
                self.env['ocr.document.line'].create({
                    'document_id': rec.id,
                    'sequence': 1,
                    'content': f"OCR error: {e}"
                })

class OcrDocumentLine(models.Model):
    _name = 'ocr.document.line'
    _description = 'OCR Document Line'
    _order = 'sequence'

    document_id = fields.Many2one('ocr.document', ondelete='cascade')
    sequence = fields.Integer()
    content = fields.Char(string='Extracted Content')
