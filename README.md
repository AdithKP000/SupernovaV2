# Supernova - Agentic RAG Pipeline

Supernova is an advanced Agentic Retrieval-Augmented Generation (RAG) system. It utilizes a multi-agent orchestrated pipeline to dynamically handle user queries, execute hybrid search strategies on scraped data, and synthesize highly accurate answers with an automated critic loop for self-correction.

## Architecture

The pipeline consists of the following modular AI agents working in sequence:

1. **Intent Agent** (`intent_agent/`): Analyzes the incoming user query and detects the underlying intent (e.g., FACTUAL, PROCEDURAL, NAVIGATIONAL) to route the search strategy appropriately.
2. **Query Reformulator** (`querry_reformulation/`): Uses an LLM to rewrite and optimize the user's initial query into a highly contextualized search string based on the detected intent.
3. **Hybrid Search Engine** (`tech_crawler/hybrid_search.py`): Combines lexical search (BM25) and semantic vector search (FAISS with `BAAI/bge-m3` embeddings), reranking the combined results using Reciprocal Rank Fusion (RRF). It defaults to exact-URL matching for NAVIGATIONAL intents.
4. **Generator Agent** (`generator_agent/`): Synthesizes a factual markdown answer using the retrieved context and the user query via Groq's high-speed open-source models (configured for `openai/gpt-oss-120b`). It is strictly prompted not to hallucinate facts missing from the context.
5. **Critic Agent** (`critic_agent/`): Evaluates the generated answer against the input query to ensure quality and relevance. If the answer fails the evaluation, the critic dynamically injects feedback into the pipeline and triggers a retry loop (up to 3 iterations) to refine the query and generate a better answer.

## Prerequisites

*   Python 3.9+
*   [Groq API Key](https://console.groq.com/) for LLM inference (Query Reformulation, Generation, and Criticism).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AdithKP000/Supernova.git
   cd Supernova
   ```

2. **Set up a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   # On MacOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Data Indexing

The hybrid search module requires vectorized databases to function (`bm25_index.pkl`, `tech_bge.index`, and `tech_bge_meta.json`). 

These files are generated via Scrapy in the `tech_crawler` module. If you are starting fresh without the indexes in the repo, you'll need to run the respective scraper and index builder functions (`clean_and_chunk.py`, `build_bm25_index.py`, `build_bge_faiss_index.py`) found in `/tech_crawler`.

## Usage

You interact with the pipeline via the root orchestrator script: `app.py`.

### Interactive Mode
If you run the script with no arguments, it launches a persistent terminal prompt allowing you to enter queries dynamically:
```bash
python app.py
```

### Direct Query Execution
You can pass questions directly from the terminal using the `--query` flag:
```bash
python app.py --query "What is BGE and how does it compare to BM25?"
```

### Disabling the Critic Loop
By default, the Agentic pipeline self-corrects based on Critic feedback. If you want to bypass the iterative reinforcement loop and get the immediate first-pass LLM generation, use the `--no-critic` flag:
```bash
python app.py --query "Google.com" --no-critic
```
