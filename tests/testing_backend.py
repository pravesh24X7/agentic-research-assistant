import os

from backend import get_workflow
from src.utils.generate_uuid import get_unique_id
from src.utils.logger import get_logger


UNIQUE_SESSION_ID=get_unique_id()
CONFIG={
    'configurable': {
        'thread_id': UNIQUE_SESSION_ID
    },
    'metadata': {
        'thread_id': UNIQUE_SESSION_ID
    },
    'run_name': 'testing_backend'
}

def main():

    logger = get_logger()
    logger.debug('\n\n[*] Begin Execution ...')

    workflow = get_workflow()

    while True:
        user_query = input(' [HUMAN] : ').strip()

        if user_query == 'exit':
            break
            
        initial_state = {
            'query': user_query,
            'max_iterations': 5,
            'iterations': 0
        }
    
        for message_chunk, _ in workflow.stream(initial_state, config=CONFIG, stream_mode="messages"):
            if message_chunk.content:
                print(message_chunk.content, end="", flush=True)
        
        print("\n", "-"*50)
        final_state = workflow.get_state(config=CONFIG).values
    
        for ans in final_state['draft_answer']:
            print(ans, end="\n"+"-----"*30+"\n")

if __name__ == '__main__':
    main()