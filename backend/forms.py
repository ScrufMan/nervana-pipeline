from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from elastic import get_all_datasets
from backend import es


class SearchForm(FlaskForm):
    search_term = StringField("Hledat:", validators=[DataRequired(), Length(min=1)],
                              render_kw={"placeholder": "Zadejte hledaný výraz"})
    dataset = SelectField('Datová sada:', validators=[DataRequired()])
    entity_type = SelectField('Typ:', validators=[DataRequired()])
    submit = SubmitField("Hledat")

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.dataset.choices = ["Všechny"] + get_all_datasets(es)
        self.entity_type.choices = ["Všechny", "Osoba", "Telefonní číslo", "Emailová adresa", "Datum", "Číslo účtu",
                                    "BTC adresa", "Lokace", "Organizace", "Internetový odkaz"]
