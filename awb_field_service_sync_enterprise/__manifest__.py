{
    'name': 'AWB Field ServiceSync',
    'version': '15.0.0.1',
    'category': 'Projects',
    'summary': 'Field Service Sync From Enterprise to Community',
    'description': """
                    
                    """,
    'author': 'Achieve Without Borders, Inc.',
    'website': "http://www.achievewithoutborders.com",
    'company': 'Achieve Without Borders, Inc.',
    'depends': ['base', 'web', 'industry_fsm'],
    'data': ['security/ir.model.access.csv',
             'data/xmlrpc_data.xml',
             'views/field_service_sync.xml',
             ],
             
    'qweb': [],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
