from odoo import fields, models

class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag Training"
    _order = "name"

    _sql_constraints = [('check_unique_tag', 'UNIQUE(name)',
                         'Property Tag needs to be UNIQUE.')]

    name = fields.Char(required=True)
    color = fields.Integer('Color')