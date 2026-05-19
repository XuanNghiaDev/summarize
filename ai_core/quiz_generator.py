import re
import random
import math
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

from ai_core import preprocessing


def split_sentences(text, lang='vi'):
    if lang == 'vi':
        return preprocessing.split_sentences_vi(text)
    return preprocessing.split_sentences_en(text)


def extract_keywords(sentences, top_k=30):
    if not sentences:
        return []
    vec = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
    X = vec.fit_transform(sentences)
    scores = X.sum(axis=0).A1
    terms = vec.get_feature_names_out()
    ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    return [t for t, s in ranked[:top_k]]


ENTITY_PATTERNS = [
    (r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", 'DATE'),
    (r"\b(?:19|20)\d{2}\b", 'YEAR'),
    (r"\b\d+[\d,\.]*%?\b", 'NUMBER'),
    (r"([A-ZĐ][\wĐ]+(?:\s+[A-ZĐ][\wĐ]+)*)", 'PROPER'),
]


def find_entities(text):
    found = []
    for pat, label in ENTITY_PATTERNS:
        for m in re.finditer(pat, text):
            span = m.group(0).strip()
            # ignore very short single letters
            if len(span) > 1:
                found.append((span, label))
    return found


def score_sentences(sentences, keywords):
    kwset = set(keywords)
    scores = []
    for s in sentences:
        words = re.findall(r"\w+", s.lower())
        sc = sum(1 for w in words if w in kwset)
        scores.append(sc + 0.1 * len(words))
    return scores


def generate_distractors(answer, pool, n=3):
    # numeric distractors
    distractors = set()
    if re.match(r"^\d+[\d,\.]*%?$", answer):
        base = re.sub(r"[^0-9]", "", answer)
        try:
            num = int(base)
            for delta in [ -10, -5, 5, 10, 20 ]:
                distractors.add(str(max(0, num + delta)))
        except Exception:
            pass

    # pull similar-length items from pool
    pool_items = [p for p in pool if p != answer]
    random.shuffle(pool_items)
    for p in pool_items:
        if len(distractors) >= n:
            break
        if p.lower() != answer.lower():
            distractors.add(p)

    # fallback synthetic variants
    while len(distractors) < n:
        distractors.add(answer + ' ' + str(random.randint(1, 99)))

    return list(distractors)[:n]


def make_question_from_sentence(sentence, answer, qtype='mcq'):
    question = None
    explanation = f"Answer extracted from sentence: {sentence}"
    if qtype == 'mcq' or qtype == 'short':
        # simple blank
        question = sentence.replace(answer, '_____')
        if question == sentence:
            question = sentence + ' What is the missing information?'
    elif qtype == 'tf':
        question = sentence
    elif qtype == 'fill':
        question = sentence.replace(answer, '_____')
    else:
        question = sentence

    return question, explanation


def generate_quiz(text, quiz_type='mcq', num_questions=5, lang='vi', difficulty='medium'):
    sentences = split_sentences(text, lang)
    if not sentences:
        return []

    keywords = extract_keywords(sentences, top_k=40)
    entities = find_entities(text)
    entity_values = [e for e, _ in entities]

    scores = score_sentences(sentences, keywords)
    ranked_idx = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)

    questions = []
    seen_questions = set()

    for idx in ranked_idx:
        if len(questions) >= num_questions:
            break
        sent = sentences[idx]
        # find candidate answers in sentence
        cands = [e for e in entity_values if e in sent]
        if not cands:
            # fallback: pick high-tfidf keyword in sentence
            words = extract_keywords([sent], top_k=10)
            if words:
                cands = [words[0]]
            else:
                continue

        answer = cands[0]
        qtext, explanation = make_question_from_sentence(sent, answer, qtype=quiz_type)
        if not qtext or qtext.strip() in seen_questions:
            continue

        item = {
            'question': qtext.strip(),
            'type': quiz_type,
            'source_sentence': sent.strip(),
            'correct_answer': answer.strip(),
            'explanation': explanation,
            'difficulty': difficulty,
        }

        if quiz_type == 'mcq':
            distractors = generate_distractors(answer, entity_values, n=3)
            options = [answer] + distractors
            random.shuffle(options)
            item['options'] = options
        elif quiz_type == 'tf':
            # randomly decide true/false by keeping or altering
            is_true = random.random() > 0.2
            if not is_true:
                # alter answer to a distractor
                distractors = generate_distractors(answer, entity_values, n=1)
                altered = distractors[0]
                item['question'] = sent.replace(answer, altered)
                item['correct_answer'] = False
            else:
                item['correct_answer'] = True
        elif quiz_type == 'fill':
            item['blank'] = '_____'
        else:
            pass

        seen_questions.add(item['question'])
        questions.append(item)

    # ensure we have exactly num_questions (if not, trim/pad)
    return questions[:num_questions]


if __name__ == '__main__':
    sample = """
    Nghị quyết 57 được ban hành vào năm 2021, do Bộ Khoa học đưa ra.
    Công ty ABC đạt doanh thu 1,000 tỷ đồng năm 2023.
    """
    print(generate_quiz(sample, quiz_type='mcq', num_questions=3, lang='vi'))
