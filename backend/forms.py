from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FieldList, SelectMultipleField, widgets, FormField
from wtforms.validators import DataRequired, Length

from backend import es
from elastic import get_all_datasets

entity_types_choices = [
    ("person", "Osoba"),
    ("datetime", "Datum"),
    ("location", "Lokace"),
    ("bank_account", "Číslo účtu"),
    ("btc_adress", "BTC adresa"),
    ("phone", "Telefonní číslo"),
    ("email", "Emailová adresa"),
    ("link", "Internetový odkaz"),
    ("organization", "Organizace"),
    ("document", "Dokument"),
    ("product", "Produkt")
]


class SearchForm(FlaskForm):
    search_terms = FieldList(StringField("Hledat:", validators=[DataRequired(), Length(min=1)],
                                         render_kw={"placeholder": "Zadejte hledaný výraz",
                                                    "oninput": "checkSearchTerm(this)"}),
                             min_entries=1)

    dataset = SelectField('Datová sada:', validators=[DataRequired()],
                          choices=[("_all", "Všechny")] + get_all_datasets(es))

    entity_types_list = FieldList(SelectMultipleField("Typ entity", choices=entity_types_choices,
                                                      widget=widgets.Select(),
                                                      option_widget=widgets.CheckboxInput()),
                                  min_entries=1)

    results_per_page = SelectField("Výsledků na stránku", validators=[DataRequired()], choices=[(10, 10), (20, 20), (50, 50), (100, 100)], default=10)

    submit = SubmitField("Hledat")
