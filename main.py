from dotenv import load_dotenv

from src.rag.ingestion import create_vector_store
from src.embedding.embedding_model import get_model
from src.utils.logger import get_logger


load_dotenv()


def main():

    console_logger = get_logger()
    console_logger.debug('[*] Begin Execution')

    console_logger.debug("[*] Loading Embedding model")
    embedding_model = get_model()

    console_logger.debug("[*] Creating Vector Store")
    vector_store = create_vector_store(
        storepath='./vector_store',
        filepath='./data/raw/data001.json',
        embedding_model=embedding_model
    )

    console_logger.debug("[*] Execution complete")



if __name__ == "__main__":
    main()