import json
from src.utils.logger import get_logger
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

logger = get_logger()


def load_file(name: str):
    """
    Loads prompt JSON safely and converts it into
    PromptTemplate or ChatPromptTemplate.
    """

    try:
        with open(name, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Debug
        logger.debug(f"[+] Raw prompt keys: {list(data.keys())}")

        # -----------------------------------
        # Standard PromptTemplate
        # -----------------------------------
        if "template" in data and "input_variables" in data:
            logger.debug("[+] Loading as PromptTemplate")
            return PromptTemplate(
                template=data["template"],
                input_variables=data["input_variables"]
            )

        # -----------------------------------
        # ChatPromptTemplate
        # -----------------------------------
        elif "messages" in data:
            logger.debug("[+] Loading as ChatPromptTemplate")

            messages = []

            for msg in data["messages"]:
                role = msg.get("role")
                content = msg.get("content")

                if not role or not content:
                    continue

                if role.lower() == "system":
                    messages.append(("system", content))

                elif role.lower() in ["human", "user"]:
                    messages.append(("human", content))

                elif role.lower() in ["ai", "assistant"]:
                    messages.append(("ai", content))

            if not messages:
                raise ValueError("No valid messages found in prompt file.")

            return ChatPromptTemplate.from_messages(messages)

        else:
            raise ValueError(
                f"Unsupported prompt schema in file: {name}"
            )

    except Exception as e:
        logger.exception(f"[-] Failed loading prompt file: {name}")
        raise RuntimeError(
            f"Prompt loading failed for {name}: {str(e)}"
        )