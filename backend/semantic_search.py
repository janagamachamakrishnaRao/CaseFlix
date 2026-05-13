from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_search(query, incident_data):

    if not incident_data:
        return []

    documents = []

    for item in incident_data:

        metadata = item["metadata"]

        text = f"""
        {item['filename']}
        {metadata['incident_type']}
        {metadata['department']}
        {metadata['summary']}
        """

        documents.append(text)

    document_embeddings = model.encode(documents)

    query_embedding = model.encode([query])

    similarities = cosine_similarity(
        query_embedding,
        document_embeddings
    )[0]

    ranked_results = np.argsort(similarities)[::-1]

    results = []

    for idx in ranked_results:

        if similarities[idx] > 0.25:

            results.append({
                "score": float(similarities[idx]),
                "data": incident_data[idx]
            })

    return results