# -*- coding: utf-8 -*-
{
    'name': "tonkho",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','dai_tgg'],
    #'css': ['static/src/css/style.css'], 
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
#         'views/tonkho.xml',
        'security/security.xml',
        'views/stock_quant.xml',
        'views/stock_picking.xml',
        'views/tonkho_stock.xml',
        'report/pick_operation_report.xml',
        #'views/assets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}