import asyncio
from asyncio import Semaphore
from typing import TYPE_CHECKING

from httpx import AsyncClient
from lingua.language import Language

from entity_recognizer.post_processor import find_btc_adresses, find_bank_accounts
from utils.text import split_string
from . import Entity
from .nametag import run_nametag

# from .spacy import get_entities

# prevent cyclic import
if TYPE_CHECKING:
    from file_processor import File


async def do_ner(client: AsyncClient, plaintext: str, language: Language) -> list[Entity]:
    match language:
        case Language.CZECH | Language.SLOVAK | Language.ENGLISH | Language.DUTCH | \
             Language.GERMAN | Language.SPANISH | Language.UKRAINIAN:
            batch_entities = await run_nametag(client, plaintext, language)
        # case _:
        #     batch_entities = get_entities(plaintext)

    batch_entities.extend(find_btc_adresses(plaintext))
    batch_entities.extend(find_bank_accounts(plaintext))
    return batch_entities


async def do_ner_with_semaphore(sem: Semaphore, client: AsyncClient, plaintext: str, language: Language):
    async with sem:  # Acquire semaphore
        return await do_ner(client, plaintext, language)


async def find_entities_in_file(client: AsyncClient, file: "File") -> list[Entity]:
    # Create a semaphore with a limit of 2 for this specific file
    sem = Semaphore(2)

    plaintext = file.plaintext
    entities = []

    # split large texts into smaller batches
    if len(plaintext) > 500000:
        batches = split_string(plaintext, 500000)
        n_batches = len(batches)
        tasks = [do_ner_with_semaphore(sem, client, batch, file.language) for batch in batches]

        finished_tasks = 0
        for completed_task in asyncio.as_completed(tasks):
            batch_entities = await completed_task
            entities.extend(batch_entities)
            finished_tasks += 1
            print(f"{file}: Finished batch {finished_tasks}/{n_batches}")
    else:
        entities = await do_ner(client, plaintext, file.language)

    return entities
