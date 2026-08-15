# NLP Model Evaluation

This document explains which NLP models were chosen for each task, and the
tradeoffs made between speed, accuracy, and resource usage.

## 1. Sentiment Analysis — VADER

**Choice:** `vaderSentiment` (rule/lexicon-based, not a neural model)

- **Speed:** Extremely fast — near-instant, no GPU or model loading needed.
- **Accuracy:** Good for short, informal chat-style text (it was specifically
  built for social-media-like language). Less accurate on long, nuanced,
  or sarcastic text compared to a fine-tuned transformer model.
- **Tradeoff:** Chosen over a transformer sentiment model (e.g. DistilBERT
  fine-tuned on SST-2) because it requires no model download, runs in
  milliseconds, and is accurate enough for support-chat-style text where
  sentiment is usually explicit.

## 2. Named Entity Recognition — spaCy (`en_core_web_sm`)

**Choice:** spaCy's small English pipeline

- **Speed:** Fast — a few milliseconds per conversation on CPU.
- **Accuracy:** Reasonable for common entities (people, organizations) but
  the "small" model trades some accuracy for size/speed compared to
  `en_core_web_lg` or `en_core_web_trf` (transformer-based).
- **Tradeoff:** The small model was chosen to keep Docker image size and
  memory usage low, per the task's own guidance about avoiding OOM issues
  in containers. For production use with higher accuracy needs, swapping
  to `en_core_web_trf` would improve entity accuracy at the cost of more
  RAM and slower inference.

## 3. Key Phrase Extraction — spaCy Noun Chunks

**Choice:** Frequency-ranked noun chunks from spaCy's dependency parser

- **Speed:** Fast — reuses the same spaCy pipeline already loaded for NER,
  no extra model needed.
- **Accuracy:** Works well for extracting concrete topics ("my order",
  "shipping team") but can occasionally surface generic or low-value
  phrases on very short conversations.
- **Tradeoff:** Chosen over a dedicated keyword-extraction library (like
  KeyBERT, which uses embeddings) because it's lightweight and needs no
  additional model — KeyBERT would give more semantically-aware phrases
  but adds another embedding model to load and run.

## 4. Summarization — Custom Extractive Summarizer

**Choice:** Frequency-based extractive summarization (picks the highest-scoring
existing sentences, rather than generating new text)

- **Speed:** Very fast — no transformer inference required.
- **Accuracy:** Extractive summaries are limited to sentences that already
  exist in the text — they can't paraphrase or compress the way an
  abstractive model (e.g. BART, T5, or an LLM) can. On short conversations,
  the "summary" may just be the original messages verbatim.
- **Tradeoff:** A Hugging Face abstractive summarization pipeline (e.g.
  `facebook/bart-large-cnn`) would produce noticeably better, shorter
  summaries, but at the cost of a ~1.6GB model download and multi-second
  inference time per conversation — a poor fit for a lightweight local
  Docker setup. The extractive approach was chosen to keep the whole
  pipeline fast and resource-light, matching the project's constraint of
  running comfortably in a standard Docker environment.

## 5. Semantic Search Embeddings — `sentence-transformers/all-MiniLM-L6-v2`

- **Speed:** Fast — a small (~90MB) model that encodes text in
  milliseconds on CPU.
- **Accuracy:** Strong general-purpose sentence embedding quality for its
  size; well-suited for short conversational text. Larger models
  (e.g. `all-mpnet-base-v2`) offer better retrieval accuracy but are
  slower and heavier.
- **Tradeoff:** MiniLM was chosen specifically because the task's own FAQ
  recommends it for avoiding OOM issues in Docker — it strikes the best
  balance of speed, size, and semantic quality for this project's scale.

## Overall Tradeoff Summary

Every model in this pipeline was chosen to prioritize **low resource usage
and fast local inference** over maximum possible accuracy — appropriate for
a project meant to run entirely in Docker on a standard development machine.
For a production deployment with dedicated inference infrastructure (GPU
servers or hosted LLM APIs), swapping in larger transformer-based models for
summarization, NER, and sentiment would meaningfully improve output quality
at the cost of latency and infrastructure complexity.