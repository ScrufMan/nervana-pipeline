import sys

import numpy as np
from httpx import AsyncClient

from . import Entity
from .nametag import run_nametag
from .spacy import get_entities
from lingua.language import Language
from entity_recognizer.post_processor import find_btc_adresses, find_bank_accounts
from typing import TYPE_CHECKING
import pandas as pd

# Prevent cyclic import
if TYPE_CHECKING:
    from file_processor import File


async def recognize_batch(client: AsyncClient, plaintext: str, language: Language) -> list[Entity]:
    match language:
        case Language.CZECH | Language.SLOVAK | Language.ENGLISH:
            batch_entities = await run_nametag(client, plaintext, language)
        case _:
            batch_entities = get_entities(plaintext)

    batch_entities.extend(find_btc_adresses(plaintext))
    batch_entities.extend(find_bank_accounts(plaintext))
    return batch_entities


async def recognize_tabular_data(client: AsyncClient, file: "File") -> list[Entity]:
    if file.format == "csv":
        df = pd.read_csv(file.path)
    elif file.format == "xls":
        df = pd.read_excel(file.path, engine="xlrd")
    elif file.format == "xlsx":
        df = pd.read_excel(file.path, engine="openpyxl")
    else:
        raise ValueError(f"Unknown tabular file format: {file.format}! Supported formats: csv, xls, xlsx")

    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    entities = []
    n_batches = 5
    batches = np.array_split(df, n_batches)
    for i, batch in enumerate(batches):
        print(f"{file.path}: Processing batch {i + 1}/{n_batches}")
        plaintext = batch.to_string(index=False, header=False)
        batch_entities = await recognize_batch(client, plaintext, file.language)
        entities.extend(batch_entities)

    return entities


async def find_entities_in_file(client: AsyncClient, file: "File") -> list[Entity]:
    # tabular data
    if file.format in ["csv", "xls", "xlsx"]:
        try:
            return await recognize_tabular_data(client, file)
        except Exception as e:
            print(f"Error while processing tabular data trying tika plaintext: {e},", file=sys.stderr)
            return await recognize_batch(client, file.plaintext, file.language)

    return await recognize_batch(client, file.plaintext, file.language)
