from odoo import fields, models, api, _
from collections import defaultdict

class MailMessage(models.Model):
    _inherit = 'mail.message'

    lead_id = fields.Many2one('crm.lead','Lead', compute="_compute_lead", store=True)
    stage_id = fields.Many2one('crm.stage','Estapa', related='lead_id.stage_id', store=True)

    @api.depends('model')
    def _compute_lead(self):
        for m in self:
            if m.model == 'crm.lead':
                lead_id = self.env['crm.lead'].search([('id','=',int(m.res_id))])
                if lead_id:
                    m.lead_id = lead_id.id

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
    unpaid_invoice_ids = fields.One2many('account.move', compute='_compute_unpaid_invoices')
    unpaid_invoices_count = fields.Integer(compute='_compute_unpaid_invoices')
    unreconciled_aml_ids = fields.One2many('account.move.line', compute='_compute_total_due', readonly=False)
    invoice_ids = fields.One2many('account.move',related='partner_id.invoice_ids', string='Invoices', readonly=True, copy=False)
    total_due = fields.Monetary(groups='account.group_account_readonly,account.group_account_invoice,sales_team.group_sale_salesman')
    amount_credit_limit = fields.Monetary(string='Credit Limit', related='partner_id.amount_credit_limit')

    def _compute_unpaid_invoices(self):
        for lead in self:
            if lead.partner_id:
                partners_unpaid_receivable_lines = self.env['account.move.line'].search([
                    ('company_id', 'child_of', self.env.company.id),
                    ('move_id.commercial_partner_id', 'in', [lead.partner_id.id]),
                    ('parent_state', '=', 'posted'),
                    ('move_id.payment_state', 'in', ('not_paid', 'partial')),
                    ('move_id.move_type', 'in', self.env['account.move'].get_sale_types()),
                    ('account_id.account_type', '=', 'asset_receivable'),
                ]).grouped(lambda line: line.move_id.commercial_partner_id.id)
                unpaid_receivable_lines = partners_unpaid_receivable_lines.get(partner.id, self.env['account.move.line'])
                unpaid_invoices = unpaid_receivable_lines.move_id
                lead.unpaid_invoice_ids = unpaid_invoices
                lead.unpaid_invoices_count = len(unpaid_invoices)
    
    @api.depends('invoice_ids')
    @api.depends_context('company', 'allowed_company_ids')
    def _compute_total_due(self):
        due_data = defaultdict(float)
        overdue_data = defaultdict(float)
        unreconciled_aml_ids = defaultdict(list)
        for overdue, partner, blocked, amount_residual_sum, aml_ids in self.env['account.move.line']._read_group(
            domain=self._get_unreconciled_aml_domain(),
            groupby=['followup_overdue', 'partner_id', 'blocked'],
            aggregates=['amount_residual:sum', 'id:array_agg'],
        ):
            unreconciled_aml_ids[partner] += aml_ids
            if not blocked:
                due_data[partner] += amount_residual_sum
                if overdue:
                    overdue_data[partner] += amount_residual_sum

        for lead in self:
            lead.total_due = due_data.get(partner, 0.0)
            lead.total_overdue = overdue_data.get(partner, 0.0)
            lead.unreconciled_aml_ids = self.env['account.move.line'].browse(unreconciled_aml_ids.get(partner, []))

    def open_sale_product_wizard(self):
        self.ensure_one()
        wiz = self.env['acanto.productos_vendidos.wizard'].create({'cliente_id': self.partner_id.id})
        return {
            'name': "Productos vendidos",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view': [(self.env.ref('acanto.view_acanto_productos_vendidos_wizard_form').id, 'form')],
            'view_id': self.env.ref('acanto.view_acanto_productos_vendidos_wizard_form').id,
            'res_model': 'acanto.productos_vendidos.wizard',
            'target': 'new',
            'res_id': wiz.id,
        }
    
    def open_action_followup(self):
        self.ensure_one()
        return {
            'name': _("Overdue Payments for %s", self.display_name),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[self.env.ref('account_followup.customer_statements_form_view').id, 'form']],
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
        }
        
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
