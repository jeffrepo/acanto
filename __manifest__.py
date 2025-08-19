# -*- coding: utf-8 -*-
{
    'name': "Acanto",
    'summary': """
        Desarrollo para acanto""",
    'description': """
       Desarrollo para acanto
    """,
    'author': "ST",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['crm','base','account','infilefel','purchase','sale','sale_crm','sale_margin', 'account_followup', 'sales_team', 'om_credit_limit'],
    'data': [
        'views/account_move_views.xml',
        'views/acanto_view.xml',
        'report/report_voucher.xml',
        'security/security.xml',
        'views/crm_lead_views.xml',
        'views/purchase_order_views.xml',
        'report/report_contrasenia_pago.xml',
        'views/res_partner_views.xml',
        'views/account_followup_views.xml',
        #'views/res_company_views.xml',
        'views/account_payment_views.xml',
        #'views/crm_stage_views.xml',
        'report/report_metodo_pago.xml',
        'views/sale_order_views.xml',
        #'views/ir_actions_report_templates.xml',
        'views/mail_message_views.xml',
        'views/report.xml',
        'views/product_views.xml',
        'views/product_template_views.xml',
        'data/acanto_data.xml',
        'wizard/productos_vendidos_wizard.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'aplication' : False,
}
