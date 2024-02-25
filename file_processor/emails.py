from neo4j import AsyncDriver

from utils import setup_logger

logger = setup_logger(__name__)


async def index_email(neo4j_driver: AsyncDriver, sender: str, recipients: list[str], subject: str, path: str):
    query = """
        MERGE (s:Person {email: $sender})
        MERGE (e:Email {subject: $subject, path: $path})
        MERGE (s)-[:SENT]->(e)
        WITH e
        UNWIND $recipients AS recipient
        MERGE (r:Person {email: recipient})
        MERGE (e)-[:RECEIVED_BY]->(r)
        """
    parameters = {'sender': sender, 'recipients': recipients, 'subject': subject, 'path': path}
    await neo4j_driver.execute_query(query, parameters)


async def process_email(neo4j_driver: AsyncDriver, file_path, metadata):
    sender = metadata.get("Message:From-Email")
    recipients = metadata.get("Message-To")
    if not recipients:
        recipients = metadata.get("Message:Raw-Header:Delivered-To")
    if isinstance(recipients, str):
        recipients = [recipients]
    subject = metadata.get("dc:subject", "No subject")
    if sender and recipients:
        try:
            await index_email(neo4j_driver, sender, recipients, subject, file_path)
            logger.info(f"{file_path}: indexed email")
        except Exception as e:
            logger.error(f"{file_path}: Error while indexing email - {e}")
    else:
        logger.error(f"{file_path}: email doesn't have sender or recipients")
