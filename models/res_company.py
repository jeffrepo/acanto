from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    dia_pago = fields.Char (
        string='Día de pago'
    )
    
    horario_pago = fields.Char (
        string='Horario de pago'
    )

    anulado_libro_compras = fields.Boolean('Anulado libro compras')
    feel_codigo_exportador = fields.Char('Codigo exportador')
