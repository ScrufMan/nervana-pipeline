from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FieldList, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length

from backend import es
from elastic import get_all_datasets, get_stored_fileformats, get_stored_file_languages

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

language_mappings = {
    "ar": "Arabský",
    "bn": "Bengálský",
    "zh": "Čínský",
    "cs": "Český",
    "nl": "Nizozemský",
    "en": "Anglický",
    "fr": "Francouzský",
    "de": "Německý",
    "el": "Řecký",
    "hi": "Hindština",
    "hu": "Maďarština",
    "id": "Indonéština",
    "it": "Italský",
    "ja": "Japonský",
    "jv": "Jávský",
    "ko": "Korejský",
    "ms": "Malajský",
    "fa": "Perský",
    "pl": "Polský",
    "pt": "Portugalský",
    "pa": "Pandžábský",
    "ro": "Rumunský",
    "ru": "Ruský",
    "sr": "Srbský",
    "sk": "Slovenský",
    "sl": "Slovinský",
    "es": "Španělský",
    "sv": "Švédský",
    "tl": "Tagalština",
    "ta": "Tamilský",
    "te": "Telugština",
    "th": "Thajský",
    "tr": "Turecký",
    "uk": "Ukrajinský",
    "ur": "Urdština",
    "vi": "Vietnamský",
}


class SearchForm(FlaskForm):
    dataset = SelectField('Datová sada:', validators=[DataRequired()],
                          choices=[("all", "Všechny")] + get_all_datasets(es))

    results_per_page = SelectField("Výsledků na stránku", validators=[DataRequired()],
                                   choices=[(10, 10), (20, 20), (50, 50), (100, 100)], default=10)

    search_terms = FieldList(StringField("Hledat:", validators=[DataRequired(), Length(min=1)],
                                         render_kw={"placeholder": "Zadejte hledaný výraz",
                                                    "oninput": "checkSearchTerm(this)"}),
                             min_entries=1)

    entity_types_list = FieldList(SelectMultipleField("Typ entity", choices=entity_types_choices,
                                                      widget=widgets.Select(),
                                                      option_widget=widgets.CheckboxInput()),
                                  min_entries=1)

    file_format_list = FieldList(SelectMultipleField("Formát souboru",
                                                     choices=list(map(lambda filetype: (filetype, filetype),
                                                                      get_stored_fileformats(es))),
                                                     widget=widgets.Select(),
                                                     option_widget=widgets.CheckboxInput()), min_entries=1)

    file_language_list = FieldList(
        SelectMultipleField("Jazyk souboru", choices=list(
            map(lambda language: (language, language_mappings.get(language, language)), get_stored_file_languages(es))),
                            widget=widgets.Select(), option_widget=widgets.CheckboxInput()), min_entries=1)

    submit = SubmitField("Hledat")


class EntityTypeForm(FlaskForm):
    entity_type = SelectField("Typ Entity", validators=[DataRequired()],
                              choices=[("all", "Všechny")] + entity_types_choices)
