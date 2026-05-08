import re
import os

import pandas as pd


FIELDS_TO_KEEP = [
    'id', 'title', 'abstract',
    'categories', 'update_date',
    'license', 'authors_parsed'
]
CATEGORIES = ['cs.LG', 'cs.CL', 'cs.AI', 'cs.IR', 'cs.NE', 'stat.ML']
PATTERN = "|".join(
    map(re.escape, CATEGORIES)
)


def process_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    cs_rows = chunk[chunk['categories'].str.contains(PATTERN,
                                                      regex=True,
                                                      na=False)][FIELDS_TO_KEEP].copy()
    cs_rows['license'] = chunk['license'].fillna('')
    cs_rows['title'] = chunk['title'].fillna('')
    cs_rows['abstract'] = chunk['abstract'].fillna('')
    cs_rows['update_date'] = pd.to_datetime( cs_rows[ 'update_date'], errors='coerce' )

    return cs_rows


def load_efficiently(filepath: str):

    if not os.path.exists(filepath):
        raise RuntimeError(f"{filepath} Do not Exists.")
    
    for chunk in pd.read_json(filepath,
                              lines=True,
                              chunksize=100_000):
        processed = process_chunk(chunk)

        if not processed.empty:
            yield processed