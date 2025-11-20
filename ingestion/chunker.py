import re
import os
from typing import List, Dict

MAX_CHARS = 2000


def chunk_blocks(raw_blocks: List[Dict], pdf_path: str) -> List[Dict]:
    """
    Chunk PDF text blocks using paragraph merging.
    Assign a GLOBAL chunk index. Add 'source' metadata.
    """
    chunks = []
    source = os.path.basename(pdf_path)  # NEW
    global_chunk_idx = 0                 # NEW

    for block in raw_blocks:
        text = block["text"].strip()
        chapter = block.get("chapter", "Unknown")
        page = block.get("page", -1)

        paragraphs = re.split(r'\n\s*\n', text)
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # merge paragraphs until threshold
            if len(current_chunk) + len(para) < MAX_CHARS:
                current_chunk += " " + para
            else:
                global_chunk_idx += 1
                chunks.append({
                    "id": f"{source}_p{page}_c{global_chunk_idx}",
                    "source": source,        # NEW
                    "chapter": chapter,
                    "page": page,
                    "chunk_index": global_chunk_idx,
                    "text": current_chunk.strip()
                })
                current_chunk = para

        # flush last chunk
        if current_chunk:
            global_chunk_idx += 1
            chunks.append({
                "id": f"{source}_p{page}_c{global_chunk_idx}",
                "source": source,           # NEW
                "chapter": chapter,
                "page": page,
                "chunk_index": global_chunk_idx,
                "text": current_chunk.strip()
            })

    return chunks
