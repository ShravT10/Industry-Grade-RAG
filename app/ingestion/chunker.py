def chunk_text(pages, chunk_size=500, overlap=100):
    chunks = []

    for page_data in pages:
        text = page_data["text"]
        page = page_data["page"]

        words = text.split()

        start = 0

        while start < len(words):
            end = start + chunk_size # end = 0 + 500. |2| end = 400 + 500 = 900

            chunk_words = words[start:end] #words = [x,y,z] . words[0:500]. |2| words[400:900]

            chunk_text = " ".join(chunk_words) # [x,y,z] = ["x y z"]

            chunks.append({
                "page": page,
                "text": chunk_text
            })

            start += chunk_size - overlap # Start = 0 + 500 - 100 = 400

    return chunks