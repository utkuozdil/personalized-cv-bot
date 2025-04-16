def chunk_text(text, max_words=200, overlap=50):
    # Split based on lines and bullet points
    lines = text.splitlines()
    blocks = []

    current_block = []
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            # Empty line signals new block
            if current_block:
                blocks.append(" ".join(current_block))
                current_block = []
        else:
            current_block.append(stripped)

    if current_block:
        blocks.append(" ".join(current_block))

    # Now chunk word-wise
    chunks = []
    current_chunk = []
    current_len = 0

    # Process each block
    for block in blocks:
        words = block.split()
        while words:
            if current_len + len(words) <= max_words:
                current_chunk.extend(words)
                current_len += len(words)
                words = []
            else:
                # Calculate how many words we can take
                words_to_take = max_words - current_len
                if words_to_take > 0:
                    current_chunk.extend(words[:words_to_take])
                    words = words[words_to_take:]
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_len = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Add overlap
    if overlap > 0 and len(chunks) > 1:
        overlapped_chunks = []
        for i in range(len(chunks)):
            if i == 0:
                overlapped_chunks.append(chunks[i])
            else:
                prev_words = chunks[i - 1].split()[-overlap:]
                curr_words = chunks[i].split()
                overlapped_chunk = " ".join(prev_words + curr_words)
                overlapped_chunks.append(overlapped_chunk)
        return overlapped_chunks

    return chunks
