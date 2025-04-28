from odoo import models, fields, api, _

class AcantoVoucher(models.Model):
    _name = 'acanto.voucher'
    _description = 'Voucher'

    name = fields.Char(
    'Name', default=lambda self: _('New'),
    copy=False, readonly=True)
    recibimos_id = fields.Many2one('res.partner',string="Recibimos de")
    factura = fields.Char(string='Factura')
    descripcion = fields.Char(string='Descripcion')
    fecha = fields.Date(string='Fecha')
    cantidad_pago = fields.Float(string='Cantidad')
    banco_id = fields.Many2one('account.journal',string="Banco")
    cuenta_cheque = fields.Float(string='Cuenta No.')
    orden = fields.Char(string='A la orden de')
    cheque_no = fields.Char(string='No.')
    cantidad_cheque = fields.Float(string='Cantidad')
    elaborado = fields.Char(string='Elaborado por')
    autorizado = fields.Char(string='Autorizado por')
    recibido = fields.Char(string='Recibido por')
    linea_ids = fields.One2many('acanto.voucher.linea', 'voucher_id', string="Lineas")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('acanto.voucher')
        return super().create(vals)

class AcantoVoucherLinea(models.Model):
    _name = 'acanto.voucher.linea'
    _description = 'Voucher Linea'

    voucher_id = fields.Many2one('acanto.voucher', string="Voucher")
    name = fields.Char('Descripcion')
    total = fields.Float('Total')

class StockRuleInherit(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values):
        res = super()._get_stock_move_values(product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values)

        sale_line_id = self.env["sale.order.line"].search([("id","=", values["sale_line_id"])])
        if sale_line_id:
            res['product_uom_qty'] = product_qty + sale_line_id.discounted_product
        return res


from odoo import models, fields

class AcantoProductosVendidos(models.TransientModel):
    _name = 'acanto.productos_vendidos'
    
    fecha = fields.Date(string="Fecha")
    factura_id = fields.Many2one("account.move", string="Factura")
    producto_id = fields.Many2one("product.product",string="Producto")
    cantidad = fields.Float("Cantidad")
    precio_unitario = fields.Float("Precio unitario")