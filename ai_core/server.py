import logging
import math
import sys
import time
import traceback
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from rouge_score import rouge_scorer

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

MODEL_DIRS = [ROOT_DIR / 'ai_core' / 'models', ROOT_DIR / 'models']

from ai_core import textrank, bilstm_extractive, preprocessing, quiz_generator

MODEL_OPTIONS = ['textrank', 'bilstm']
LANG_OPTIONS = ['vi', 'en']

SUMMARY_LENGTH_MIN = 10
SUMMARY_LENGTH_MAX = 100
DEFAULT_SUMMARY_LENGTH = 40

cache = {
    'bilstm': {},
}

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)


def error_response(message, status_code=400):
    return jsonify({'success': False, 'error': message}), status_code


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


def validate_model(model):
    if model not in MODEL_OPTIONS:
        return 'Unsupported model'
    return None


def validate_payload(payload):
    text = payload.get('text', '')
    model = payload.get('model', 'textrank')
    lang = payload.get('lang', 'vi')
    summary_length = normalize_summary_length(payload.get('summary_length'))

    if not isinstance(text, str) or len(text.strip()) < 20:
        return 'Text is required and must contain at least 20 characters.'

    model_error = validate_model(model)
    if model_error:
        return model_error

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
    raise FileNotFoundError(
        f"Model file '{filename}' not found. Train with: python run_pipeline.py {filename.split('_')[1].split('.')[0]}"
    )


def load_bilstm(lang):
    if lang in cache['bilstm']:
        return cache['bilstm'][lang]

    model_path = resolve_model_path(f'bilstm_{lang}.pt')
    model, vectorizer = bilstm_extractive.load_model(str(model_path))
    cache['bilstm'][lang] = (model, vectorizer)
    return model, vectorizer


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


def run_summarization(text, model, lang, summary_length):
    """Run TextRank or BiLSTM extractive summarization."""
    model_error = validate_model(model)
    if model_error:
        raise ValueError(model_error)

    sentences = split_sentences(text, lang)

    if not sentences:
        return text.strip()

    num_sentences = max(
        1,
        min(len(sentences), math.ceil(len(sentences) * summary_length / 100)),
    )

    if model == 'textrank':
        summary, _ = textrank.summarize(sentences, num_sentences=num_sentences)
        return summary

    model_obj, vectorizer = load_bilstm(lang)
    return bilstm_extractive.predict(
        sentences, model_obj, vectorizer, num_sentences=num_sentences
    )


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
            except Exception as exc:
                raise ValueError('Failed to extract text from PDF.') from exc
    elif filename.endswith('.docx') or file.mimetype in (
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ):
        try:
            from docx import Document
            from io import BytesIO
            file.stream.seek(0)
            doc = Document(BytesIO(file.read()))
            paras = [p.text for p in doc.paragraphs]
            text = '\n'.join(paras)
        except Exception as exc:
            raise ValueError('Failed to extract text from DOCX.') from exc
    elif filename.endswith('.txt') or (file.mimetype and file.mimetype.startswith('text')):
        try:
            file.stream.seek(0)
            raw = file.read()
            if isinstance(raw, bytes):
                text = raw.decode('utf-8', errors='replace')
            else:
                text = raw
        except Exception as exc:
            raise ValueError('Failed to read text file.') from exc
    else:
        raise ValueError('Unsupported file type. Only PDF, DOCX and TXT are allowed.')

    lines = [ln.strip() for ln in (text or '').splitlines() if ln and ln.strip()]
    cleaned = ' '.join(lines)
    return ' '.join(cleaned.split())


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'models': MODEL_OPTIONS})


@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        if 'document' not in request.files:
            return error_response('No document file provided.', 400)

        file = request.files['document']
        if not file or file.filename == '':
            return error_response('No document file provided.', 400)

        if request.content_length and request.content_length > 10 * 1024 * 1024:
            return error_response('File too large (max 10MB).', 400)

        model = request.form.get('model', 'textrank')
        lang = request.form.get('lang', 'vi')
        summary_length = normalize_summary_length(request.form.get('summary_length'))

        model_error = validate_model(model)
        if model_error:
            return error_response(model_error, 400)
        if lang not in LANG_OPTIONS:
            return error_response(f"Language must be one of: {', '.join(LANG_OPTIONS)}", 400)
        if summary_length is None:
            return error_response(
                f"Summary length must be an integer between {SUMMARY_LENGTH_MIN} and {SUMMARY_LENGTH_MAX}.",
                400,
            )

        text = extract_text_from_file(file)
        if not text or len(text.strip()) < 20:
            return error_response('Extracted text is too short or empty.', 400)

        start = time.time()
        summary = run_summarization(text, model, lang, summary_length)
        elapsed = int((time.time() - start) * 1000)

        return jsonify({
            'success': True,
            'summary': summary,
            'model': model,
            'lang': lang,
            'summary_length': summary_length,
            'time_ms': elapsed,
            'sourceFile': file.filename,
        })
    except ValueError as err:
        logger.warning('[upload] %s', err)
        return error_response(str(err), 400)
    except FileNotFoundError as err:
        logger.error('[upload] %s', err)
        return error_response(str(err), 503)
    except Exception as err:
        logger.error('[upload] %s\n%s', err, traceback.format_exc())
        return error_response(str(err), 500)


@app.route('/generate-quiz', methods=['POST'])
def generate_quiz_route():
    try:
        payload = request.get_json(force=True) or {}
        text = payload.get('text', '')
        quiz_type = payload.get('quiz_type', 'mcq')
        num_questions = int(payload.get('num_questions', 5) or 5)
        lang = payload.get('lang', 'vi')
        difficulty = payload.get('difficulty', 'medium')

        if not isinstance(text, str) or len(text.strip()) < 20:
            return error_response(
                'Text is required and must contain at least 20 characters.', 400
            )

        num_questions = max(1, min(50, num_questions))
        questions = quiz_generator.generate_quiz(
            text,
            quiz_type=quiz_type,
            num_questions=num_questions,
            lang=lang,
            difficulty=difficulty,
        )
        return jsonify({'success': True, 'questions': questions, 'count': len(questions)})
    except Exception as err:
        logger.error('[generate-quiz] %s\n%s', err, traceback.format_exc())
        return error_response(str(err), 500)


@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        payload = request.get_json(force=True) or {}
        error = validate_payload(payload)
        if error:
            status = 400
            return error_response(error, status)

        text = payload['text'].strip()
        model = payload['model']
        lang = payload['lang']
        reference = payload.get('reference')
        summary_length = normalize_summary_length(payload.get('summary_length'))

        start = time.time()
        summary = run_summarization(text, model, lang, summary_length)
        elapsed = int((time.time() - start) * 1000)
        rouge = compute_rouge(summary, reference)

        return jsonify({
            'success': True,
            'summary': summary,
            'rouge': rouge,
            'model': model,
            'lang': lang,
            'summary_length': summary_length,
            'time_ms': elapsed,
        })
    except ValueError as err:
        logger.warning('[summarize] %s', err)
        return error_response(str(err), 400)
    except FileNotFoundError as err:
        logger.error('[summarize] %s', err)
        return error_response(str(err), 503)
    except Exception as err:
        logger.error('[summarize] %s\n%s', err, traceback.format_exc())
        return error_response(str(err), 500)


@app.route('/upload-quiz', methods=['POST'])
def upload_quiz():
    try:
        if 'file' not in request.files:
            return error_response('No file provided.', 400)

        file = request.files['file']
        if file.filename == '':
            return error_response('Empty filename.', 400)

        max_size = 10 * 1024 * 1024
        if request.content_length and request.content_length > max_size:
            return error_response('File too large (max 10MB).', 400)

        quiz_type = request.form.get('quiz_type', 'mcq')
        try:
            num_questions = int(request.form.get('num_questions', 5) or 5)
        except (TypeError, ValueError):
            num_questions = 5
        summarize_first = request.form.get('summarize_first', 'false').lower() in (
            '1', 'true', 'yes'
        )
        summary_length = request.form.get('summary_length')
        lang = request.form.get('language', 'vi')

        text = extract_text_from_file(file)
        if not text or len(text) < 20:
            return error_response('Extracted text is too short.', 400)

        text_for_quiz = text
        if summarize_first:
            s_len = normalize_summary_length(summary_length)
            if s_len is None:
                s_len = DEFAULT_SUMMARY_LENGTH
            text_for_quiz = run_summarization(text, 'textrank', lang, s_len)

        num_questions = max(1, min(50, num_questions))
        questions = quiz_generator.generate_quiz(
            text_for_quiz,
            quiz_type=quiz_type,
            num_questions=num_questions,
            lang=lang,
        )
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions),
            'extracted_text': text,
        })
    except ValueError as err:
        logger.warning('[upload-quiz] %s', err)
        return error_response(str(err), 400)
    except Exception as err:
        logger.error('[upload-quiz] %s\n%s', err, traceback.format_exc())
        return error_response(str(err), 500)


if __name__ == '__main__':
    import os

    port = int(os.environ.get('PORT', 5000))
    print(f'[AI Core] Starting Flask server on http://localhost:{port}')
    print(f'[AI Core] Supported models: {", ".join(MODEL_OPTIONS)}')
    app.run(host='0.0.0.0', port=port)
