{
    'name': 'OWL_Tutorial',
    'version': '1.0',
    'category': 'OWL',
    'sequence': -1,
    'depends': ['base', 'web'],
    'installable': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/todo_list_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'owl/static/src/components/*/*.js',
            'owl/static/src/components/*/*.xml',
            'owl/static/src/components/*/*.scss',
        ],
    },
}