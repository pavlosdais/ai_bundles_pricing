# AI-Powered Bundling & Pricing Strategist

- `dataset.xlsx`: The dataset containing the products.
- `generate_dataset.py`: Preprocess the .xsls data into .csv format.
- `qwen_predict.ipynb`: Augments the item.csv with the names, categories of the products. Also adds complemantory items for bundles using the `qwen2.5-14b-awq` LLM.
- `embed_faiss.ipynb`: (Part 1) Projects names into the embedding space and searches for complemantary items that exist in our dataset in the embedding space using `faiss`. 
- `final_recommendation.ipynb`: (Part 2) Using the complemantary items generated from part 1, we make personalized bundles to the user using the user preference, market behavior, item stock etc.

All code was run on Kaggle and needs path modifications to run locally.

## Members
- Themis Marinaki
- Aristarchos Kaloutsas
- Panagiotis Kanellopoulos
- Pavlos Ntais