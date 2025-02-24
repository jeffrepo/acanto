from odoo import fields, models, api


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    def _calcular_saldo(self):
        saldo = 0
        if self.partner_id:
            factura_ids = self.env['account.move'].search([('state','=', 'posted'),('move_type','=','out_invoice'),('amount_residual','>',0),('partner_id','=', self.partner_id.id)])
            for factura in factura_ids:
                saldo += factura.amount_residual
        self.saldo = saldo

    plazo_pago = fields.Many2one(
        string='plazo de pago',
        related='partner_id.property_payment_term_id', readonly=True,
    )
    fecha_inicio = fields.Date(string='Fecha Inicio')
    fecha_final = fields.Date(string='Fecha Final')
    productos_vendidos_ids = fields.Many2many('account.move.line')
    saldo = fields.Monetary('Saldo', compute= _calcular_saldo)
    currency_id = fields.Many2one(related='company_id.currency_id', depends=["company_id"], store=True)

    @api.depends('partner_id')
    def _compute_name(self):
        for lead in self:
            if not lead.name and lead.partner_id and lead.partner_id.name:
                lead.name = lead.partner_id.name

    @api.onchange('stage_id')
    def _onchange_estado_perdido(self):
        if self.stage_id.esta_perdida:
            self.action_set_lost(lost_reason=False)

    @api.onchange('fecha_inicio', 'fecha_final')
    def onchange_fecha(self):
        if self.fecha_inicio and self.fecha_final:
            move_lines = self.env['account.move.line'].search([
                ('move_id.invoice_date', '>=', self.fecha_inicio),
                ('move_id.invoice_date', '<=', self.fecha_final),
                ('move_id.partner_id', '=', self.partner_id.id),
                ('account_id.account_type', '=', 'income'),
                ('price_subtotal', '>', 0),
            ],order="date ASC")
            self.productos_vendidos_ids = [(6, 0, move_lines.ids)]
