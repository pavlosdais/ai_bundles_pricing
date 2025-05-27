# AI-Powered Bundling & Pricing Strategist
A complete end-to-end pipeline for generating and pricing personalized product bundles using state-of-the-art LLMs, embeddings and business logic.

- `dataset.xlsx`: The dataset containing the products.
- `generate_dataset.py`: Preprocess the .xsls data into .csv format.
- `qwen_predict.ipynb`: Augments the item.csv with the names, categories of the products. Also adds complemantory items for bundles using the `qwen2.5-14b-awq` LLM.
- `embed_faiss.ipynb`: (Part 1) Projects names into the embedding space and searches for complemantary items that exist in our dataset in the embedding space using `faiss`. 
- `final_recommendation.ipynb`: (Part 2) Using the complemantary items generated from part 1, we make personalized bundles to the user using the user preference, market behavior, item stock etc.

All code was run on Kaggle and needs path modifications to run locally.

## Key Features
1. Embedding & Similarity Search
- SentenceTransformer → 384-dim embeddings of product titles
- FAISS index for sub-millisecond nearest-neighbor lookups
- Uncover “hidden” complementary relationships in your catalog

2. Smart Bundling & Pricing
- User profiles: average spend, past purchases, taste-vectors
- Bundle feature-engineering: price context, category, stock, co-buy patterns
- Interpretable linear scoring with tunable weights
- Margin- and stock-aware discount engine (5–40% range)

## Team Members
- [Themis Marinaki](https://github.com/marinakithemis)
- [Aristarchos Kaloutsas](https://github.com/aristarhoskal)
- [Panagiotis Kanellopoulos](https://github.com/kanellopoulosP)
- [Pavlos Ntais](https://github.com/pavlosdais)
