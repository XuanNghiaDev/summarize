import math
import sys
import time
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from rouge_score import rouge_scorer
import io

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

app = Flask(__name__)
CORS(app)

MODEL_DIRS = [ROOT_DIR / 'ai_core' / 'models', ROOT_DIR / 'models']

# Import wrapper modules from ai_core package.
from ai_core import textrank, bilstm_extractive, seq2seq_abstractive, preprocessing, quiz_generator

MODEL_OPTIONS = ['textrank', 'bilstm', 'seq2seq']
LANG_OPTIONS = ['vi', 'en']

SUMMARY_LENGTH_MIN = 10
SUMMARY_LENGTH_MAX = 100
DEFAULT_SUMMARY_LENGTH = 40

cache = {
    'bilstm': {},
    'seq2seq': {},
}

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)


def normalize_summary_length(value):
    if value is None:
        return DEFAULT_SUMMARY_LENGTH
    try:
        summary_length = int(value)
    except (TypeError, ValueError):
        return None
    if summary_length < SUMMARY_LENGTH_MIN or summary_length > SUMMARY_LENGTH_MAX:
        return None
    return summary_length


def validate_payload(payload):
    text = payload.get('text', '')
    model = payload.get('model', 'textrank')
    lang = payload.get('lang', 'vi')
    summary_length = normalize_summary_length(payload.get('summary_length'))

    if not isinstance(text, str) or len(text.strip()) < 20:
        return 'Text is required and must contain at least 20 characters.'
    if model not in MODEL_OPTIONS:
        return f"Model must be one of: {', '.join(MODEL_OPTIONS)}"
    if lang not in LANG_OPTIONS:
        return f"Language must be one of: {', '.join(LANG_OPTIONS)}"
    if summary_length is None:
        return f"Summary length must be an integer between {SUMMARY_LENGTH_MIN} and {SUMMARY_LENGTH_MAX}."
    return None


def resolve_model_path(filename):
    for dir_path in MODEL_DIRS:
        candidate = dir_path / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(filename)


def load_bilstm(lang):
    if lang in cache['bilstm']:
        return cache['bilstm'][lang]

    model_path = resolve_model_path(f'bilstm_{lang}.pt')
    model, vectorizer = bilstm_extractive.load_model(str(model_path))
    cache['bilstm'][lang] = (model, vectorizer)
    return model, vectorizer


def load_seq2seq(lang):
    if lang in cache['seq2seq']:
        return cache['seq2seq'][lang]

    model_path = resolve_model_path(f'seq2seq_{lang}.pt')
    model, vocab = seq2seq_abstractive.load_model(str(model_path))
    cache['seq2seq'][lang] = (model, vocab)
    return model, vocab


def compute_rouge(summary, reference):
    if not reference or not isinstance(reference, str):
        return None
    scores = scorer.score(reference, summary)
    return {
        'rouge1': scores['rouge1'].fmeasure,
        'rouge2': scores['rouge2'].fmeasure,
        'rougeL': scores['rougeL'].fmeasure,
    }


def split_sentences(text, lang):
    if lang == 'vi':
        return preprocessing.split_sentences_vi(text)
    return preprocessing.split_sentences_en(text)


def extract_text_from_file(file):
    filename = (file.filename or '').lower()
    text = ''
    if filename.endswith('.pdf') or file.mimetype == 'application/pdf':
        try:
            import pdfplumber
            file.stream.seek(0)
            with pdfplumber.open(file.stream) as pdf:
                pages = [p.extract_text() or '' for p in pdf.pages]
            text = '\n'.join(pages)
        except Exception:
            try:
                from PyPDF2 import PdfReader
                file.stream.seek(0)
                reader = PdfReader(file.stream)
                pages = [p.extract_text() or '' for p in reader.pages]
                text = '\n'.join(pages)
            except Exception:
                raise ValueError('Failed to extract text from PDF.')
    elif filename.endswith('.docx') or file.mimetype in ('application/vnd.openxmlformats-officedocument.wordprocessingml.document',):
        try:
            from docx import Document
            from io import BytesIO
            file.stream.seek(0)
            doc = Document(BytesIO(file.read()))
            paras = [p.text for p in doc.paragraphs]
            text = '\n'.join(paras)
        except Exception:
            raise ValueError('Failed to extract text from DOCX.')
    elif filename.endswith('.txt') or (file.mimetype and file.mimetype.startswith('text')):
        try:
            file.stream.seek(0)
            raw = file.read()
            if isinstance(raw, bytes):
                text = raw.decode('utf-8', errors='replace')
            else:
                text = raw
        except Exception:
            raise ValueError('Failed to read text file.')
    else:
        raise ValueError('Unsupported file type. Only PDF, DOCX and TXT are allowed.')

    lines = [ln.strip() for ln in (text or '').splitlines() if ln and ln.strip()]
    cleaned = ' '.join(lines)
    cleaned = ' '.join(cleaned.split())
    return cleaned


@app.route('/upload', methods=['POST'])
def upload_document():
    if 'document' not in request.files:
        return jsonify({'error': 'No document file provided.'}), 400

    file = request.files['document']
    if not file or file.filename == '':
        return jsonify({'error': 'No document file provided.'}), 400

    if request.content_length and request.content_length > 10 * 1024 * 1024:
        return jsonify({'error': 'File too large (max 10MB).'}), 400

    model = request.form.get('model', 'textrank')
    lang = request.form.get('lang', 'vi')
    summary_length = normalize_summary_length(request.form.get('summary_length'))

    if model not in MODEL_OPTIONS:
        return jsonify({'error': f"Model must be one of: {', '.join(MODEL_OPTIONS)}"}), 400
    if lang not in LANG_OPTIONS:
        return jsonify({'error': f"Language must be one of: {', '.join(LANG_OPTIONS)}"}), 400
    if summary_length is None:
        return jsonify({'error': f"Summary length must be an integer between {SUMMARY_LENGTH_MIN} and {SUMMARY_LENGTH_MAX}."}), 400

    try:
        text = extract_text_from_file(file)
    except ValueError as err:
        return jsonify({'error': str(err)}), 400

    if not text or len(text.strip()) < 20:
        return jsonify({'error': 'Extracted text is too short or empty.'}), 400

    sentences = split_sentences(text, lang)
    start = time.time()
    if model == 'textrank':
        num_sentences = max(1, min(len(sentences), math.ceil(len(sentences) * summary_length / 100)))
        summary, _ = textrank.summarize(sentences, num_sentences=num_sentences)
    elif model == 'bilstm':
        if not sentences:
            summary = text
        else:
            model_obj, vectorizer = load_bilstm(lang)
            num_sentences = max(1, min(len(sentences), math.ceil(len(sentences) * summary_length / 100)))
            summary = bilstm_extractive.predict(sentences, model_obj, vectorizer, num_sentences=num_sentences)
    else:
        model_obj, vocab = load_seq2seq(lang)
        max_len = max(10, min(200, math.ceil(len(text.split()) * summary_length / 100)))
        summary = seq2seq_abstractive.predict(text, model_obj, vocab, max_len=max_len)

    elapsed = int((time.time() - start) * 1000)
    return jsonify({
        'summary': summary,
        'model': model,
        'lang': lang,
        'summary_length': summary_length,
        'time_ms': elapsed,
        'sourceFile': file.filename,
    })


@app.route('/generate-quiz', methods=['POST'])
def generate_quiz_route():
    payload = request.get_json(force=True)
    text = payload.get('text', '')
    quiz_type = payload.get('quiz_type', 'mcq')
    num_questions = int(payload.get('num_questions', 5) or 5)
    lang = payload.get('lang', 'vi')
    difficulty = payload.get('difficulty', 'medium')

    if not isinstance(text, str) or len(text.strip()) < 20:
        return jsonify({'error': 'Text is required and must contain at least 20 characters.'}), 400

    num_questions = max(1, min(50, num_questions))

    questions = quiz_generator.generate_quiz(text, quiz_type=quiz_type, num_questions=num_questions, lang=lang, difficulty=difficulty)
    return jsonify({'questions': questions, 'count': len(questions)})


@app.route('/summarize', methods=['POST'])
def summarize():
    payload = request.get_json(force=True)
    error = validate_payload(payload)
    if error:
        return jsonify({'error': error}), 400

    text = payload['text'].strip()
    model = payload['model']
    lang = payload['lang']
    reference = payload.get('reference')

    start = time.time()
    summary = None
    summary_length = normalize_summary_length(payload.get('summary_length'))

    if model == 'textrank':
        sentences = split_sentences(text, lang)
        num_sentences = max(1, min(len(sentences), math.ceil(len(sentences) * summary_length / 100)))
        summary, _ = textrank.summarize(sentences, num_sentences=num_sentences)
    elif model == 'bilstm':
        sentences = split_sentences(text, lang)
        if not sentences:
            summary = text
        else:
            model_obj, vectorizer = load_bilstm(lang)
            num_sentences = max(1, min(len(sentences), math.ceil(len(sentences) * summary_length / 100)))
            summary = bilstm_extractive.predict(sentences, model_obj, vectorizer, num_sentences=num_sentences)
    else:
        model_obj, vocab = load_seq2seq(lang)
        max_len = max(10, min(200, math.ceil(len(text.split()) * summary_length / 100)))
        summary = seq2seq_abstractive.predict(text, model_obj, vocab, max_len=max_len)

    elapsed = int((time.time() - start) * 1000)
    rouge = compute_rouge(summary, reference)

    return jsonify({
        'summary': summary,
        'rouge': rouge,
        'model': model,
        'lang': lang,
        'summary_length': summary_length,
        'time_ms': elapsed,
    })


@app.route('/upload-quiz', methods=['POST'])
def upload_quiz():
    try:
        # Basic validations
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided.'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename.'}), 400

        # size check
        max_size = 10 * 1024 * 1024  # 10 MB
        if request.content_length and request.content_length > max_size:
            return jsonify({'error': 'File too large (max 10MB).'}), 400

        quiz_type = request.form.get('quiz_type', 'mcq')
        try:
            num_questions = int(request.form.get('num_questions', 5) or 5)
        except Exception:
            num_questions = 5
        summarize_first = request.form.get('summarize_first', 'false').lower() in ('1', 'true', 'yes')
        summary_length = request.form.get('summary_length')
        lang = request.form.get('language', 'vi')

        # Extract text based on file type
        filename = (file.filename or '').lower()
        text = ''
        # Try PDF extraction
        if filename.endswith('.pdf') or file.mimetype == 'application/pdf':
            try:
                import pdfplumber
                file.stream.seek(0)
                with pdfplumber.open(file.stream) as pdf:
                    pages = [p.extract_text() or '' for p in pdf.pages]
                text = '\n'.join(pages)
            except Exception:
                try:
                    from PyPDF2 import PdfReader
                    file.stream.seek(0)
                    reader = PdfReader(file.stream)
                    pages = [p.extract_text() or '' for p in reader.pages]
                    text = '\n'.join(pages)
                except Exception:
                    return jsonify({'error': 'Failed to extract text from PDF.'}), 500

        elif filename.endswith('.docx') or file.mimetype in ('application/vnd.openxmlformats-officedocument.wordprocessingml.document',):
            try:
                from docx import Document
                from io import BytesIO
                file.stream.seek(0)
                doc = Document(BytesIO(file.read()))
                paras = [p.text for p in doc.paragraphs]
                text = '\n'.join(paras)
            except Exception:
                return jsonify({'error': 'Failed to extract text from DOCX.'}), 500

        elif filename.endswith('.txt') or (file.mimetype and file.mimetype.startswith('text')):
            try:
                file.stream.seek(0)
                raw = file.read()
                if isinstance(raw, bytes):
                    text = raw.decode('utf-8', errors='replace')
                else:
                    text = raw
            except Exception:
                return jsonify({'error': 'Failed to read text file.'}), 500
        else:
            return jsonify({'error': 'Unsupported file type.'}), 400

        # Clean extracted text
        lines = [ln.strip() for ln in (text or '').splitlines() if ln and ln.strip()]
        cleaned = ' '.join(lines)
        cleaned = ' '.join(cleaned.split())
        if not cleaned or len(cleaned) < 20:
            return jsonify({'error': 'Extracted text is too short.'}), 400

        # Optionally summarize
        text_for_quiz = cleaned
        if summarize_first:
            try:
                s_len = normalize_summary_length(summary_length)
            except Exception:
                s_len = DEFAULT_SUMMARY_LENGTH
            if s_len is None:
                s_len = DEFAULT_SUMMARY_LENGTH
            sentences = split_sentences(cleaned, lang)
            if not sentences:
                summary = cleaned
            else:
                num_sentences = max(1, min(len(sentences), math.ceil(len(sentences) * s_len / 100)))
                summary, _ = textrank.summarize(sentences, num_sentences=num_sentences)
                text_for_quiz = summary

        questions = quiz_generator.generate_quiz(text_for_quiz, quiz_type=quiz_type, num_questions=num_questions, lang=lang)
        return jsonify({'questions': questions, 'count': len(questions), 'extracted_text': cleaned})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import os

    port = int(os.environ.get('PORT', 5000))
    print(f'[AI Core] Starting Flask server on http://localhost:{port}')
    app.run(host='0.0.0.0', port=port)
