from dotenv import load_dotenv

from src.rag.ingestion import create_vector_store
from src.embedding.embedding_model import get_model
from src.utils.logger import get_logger
from src.config.settings import VECTOR_STORE_DIRECTORY, DATAFILE_PATH


load_dotenv()


def main():

    console_logger = get_logger()
    console_logger.debug('\n\n[*] Begin Execution')

    console_logger.debug("\n\n[*] Loading Embedding model")
    embedding_model = get_model()

    console_logger.debug("\n\n[*] Creating Vector Store")
    vector_store = create_vector_store(
        storepath=VECTOR_STORE_DIRECTORY,
        filepath=DATAFILE_PATH,
        embedding_model=embedding_model
    )

    print("Total documents stored (main fxn)", vector_store._collection.count())
    console_logger.debug("\n\n[*] Execution complete")


if __name__ == "__main__":
    main()