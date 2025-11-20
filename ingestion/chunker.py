# ingestion/chunker.py

import re
from typing import List, Dict


MAX_CHARS = 2000


def chunk_blocks(raw_blocks: List[Dict]) -> List[Dict]:
    chunks = []

    for block in raw_blocks:
        text = block["text"].strip()
        chapter = block["chapter"]
        page = block["page"]

        # Split by paragraph (double newline or single newline)
        paragraphs = re.split(r'\n\s*\n', text)

        current_chunk = ""
        chunk_idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Merge paragraphs until threshold
            if len(current_chunk) + len(para) < MAX_CHARS:
                current_chunk += " " + para
            else:
                # Save previous chunk
                chunk_idx += 1
                chunks.append({
                    "id": f"{chapter}_{page}_{chunk_idx}",
                    "chapter": chapter,
                    "page": page,
                    "chunk_index": chunk_idx,
                    "text": current_chunk.strip()
                })
                current_chunk = para  # start new chunk

        # Save last chunk
        if current_chunk:
            chunk_idx += 1
            chunks.append({
                "id": f"{chapter}_{page}_{chunk_idx}",
                "chapter": chapter,
                "page": page,
                "chunk_index": chunk_idx,
                "text": current_chunk.strip()
            })

    return chunks
