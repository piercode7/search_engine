import torch
from torch.nn.functional import softmax
from transformers import BertModel, BertTokenizer

#bad_words = ["bitch", "fuck", "fucked", "shit", "asshole", "damn", "bastard"]

def extract_sentiment(text, model=BertModel.from_pretrained('bert-base-uncased'), max_seq_length=512):
    # Tokenizzazione del testo
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokens = tokenizer.tokenize(text)

    # Limita la lunghezza dei token se supera max_seq_length
    if len(tokens) > max_seq_length:
        tokens = tokens[:max_seq_length]

    indexed_tokens = tokenizer.convert_tokens_to_ids(tokens)

    # Calcolo dell'output del modello BERT
    with torch.no_grad():
        outputs = model(torch.tensor([indexed_tokens]))

    # Estrazione delle probabilità di appartenenza a ciascuna classe (positivo/negativo)
    logits = outputs.last_hidden_state
    probs = softmax(logits, dim=2)[0, :, 1].tolist()  # Probabilità di classe positiva

    # Calcolo del rapporto tra positivo e negativo
    positive_prob = probs[1]
    negative_prob = probs[0]

    # Normalizzazione delle probabilità in un intervallo da 0 a 1
    normalized_positive_prob = positive_prob / (positive_prob + negative_prob)

    # Determinazione del sentimento in base alle probabilità
    sentiment_score = normalized_positive_prob  # Utilizza la probabilità positiva come punteggio di sentiment

    return sentiment_score
