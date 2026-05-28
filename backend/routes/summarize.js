const express = require('express');
const multer = require('multer');
const mammoth = require('mammoth');
const pdfParse = require('pdf-parse');
const router = express.Router();
const pythonBridge = require('../services/pythonBridge');
// const fs = require('fs');
// const path = require('path');

const upload = multer({ storage: multer.memoryStorage() });
const MODEL_OPTIONS = ['textrank', 'bilstm'];
const LANG_OPTIONS = ['vi', 'en'];

const ALLOWED_MIMES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];

function parseSummaryLength(value) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < 10 || parsed > 100) {
    return null;
  }
  return parsed;
}

async function extractTextFromFile(file) {
  const mime = file.mimetype;
  if (mime === 'application/pdf') {
    const data = await pdfParse(file.buffer);
    return data.text || '';
  }

  if (mime === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
    const { value } = await mammoth.extractRawText({ buffer: file.buffer });
    return value || '';
  }

  if (mime === 'text/plain') {
    return file.buffer.toString('utf-8');
  }

  throw new Error('Unsupported file type. Only PDF, DOCX and TXT are allowed.');
}

router.post('/summarize', async (req, res) => {
  try {
    const { text, model, lang, reference, summary_length } = req.body;
    const summaryLength = parseSummaryLength(summary_length ?? 40);
    if (summaryLength === null) {
      return res.status(400).json({ error: 'Summary length must be an integer between 10 and 100.' });
    }

    if (!text || typeof text !== 'string' || text.trim().length < 20) {
      return res.status(400).json({ error: 'Text is required and must be at least 20 characters.' });
    }

    if (!MODEL_OPTIONS.includes(model)) {
      return res.status(400).json({ error: 'Unsupported model' });
    }

    if (!LANG_OPTIONS.includes(lang)) {
      return res.status(400).json({ error: `Language must be one of: ${LANG_OPTIONS.join(', ')}` });
    }

    const response = await pythonBridge.summarize({ text, model, lang, reference, summary_length: summaryLength });
    res.json(response);
  } catch (error) {
    console.error('[Backend] Summarize error:', error?.message || error);
    const message = error?.message || 'Failed to summarize text. Please check Python service.';
    const status = message.includes('Could not reach Python service')
      ? 502
      : message.includes('Unsupported model') || message.includes('must be')
        ? 400
        : message.includes('not found')
          ? 503
          : 500;
    res.status(status).json({ success: false, error: message });
  }
});

router.post('/upload', upload.single('document'), async (req, res) => {
  try {
    const { model, lang, summary_length } = req.body;
    const summaryLength = parseSummaryLength(summary_length ?? 40);
    if (summaryLength === null) {
      return res.status(400).json({ error: 'Summary length must be an integer between 10 and 100.' });
    }
    const file = req.file;

    if (!file) {
      return res.status(400).json({ error: 'No document file provided.' });
    }

    if (!ALLOWED_MIMES.includes(file.mimetype)) {
      return res.status(400).json({ error: 'Unsupported file type. Only PDF, DOCX, and TXT are allowed.' });
    }

    if (!MODEL_OPTIONS.includes(model)) {
      return res.status(400).json({ error: 'Unsupported model' });
    }

    if (!LANG_OPTIONS.includes(lang)) {
      return res.status(400).json({ error: `Language must be one of: ${LANG_OPTIONS.join(', ')}` });
    }

    const text = await extractTextFromFile(file);
    if (!text || typeof text !== 'string' || text.trim().length < 20) {
      return res.status(400).json({ error: 'Extracted text is too short or empty.' });
    }

    const response = await pythonBridge.summarize({ text, model, lang, reference: null, summary_length: summaryLength });
    res.json({ ...response, sourceFile: file.originalname });
  } catch (error) {
    console.error('[Backend] Upload error:', error?.message || error);
    const message = error?.message || 'Failed to upload file and summarize.';
    const status = message.includes('Could not reach Python service') ? 502 : 500;
    res.status(status).json({ error: message });
  }
});

router.post('/generate-quiz', async (req, res) => {
  try {
    const { text, quiz_type, num_questions, lang, difficulty } = req.body;
    if (!text || typeof text !== 'string' || text.trim().length < 20) {
      return res.status(400).json({ error: 'Text is required and must be at least 20 characters.' });
    }

    const limit = Number(num_questions) || 5;
    const questionCount = Math.max(1, Math.min(50, limit));
    const quizPayload = {
      text,
      quiz_type: quiz_type || 'mcq',
      num_questions: questionCount,
      lang: lang || 'vi',
      difficulty: difficulty || 'medium',
    };

    const response = await pythonBridge.generateQuiz(quizPayload);
    res.json(response);
  } catch (error) {
    console.error('[Backend] Generate quiz error:', error?.message || error);
    const message = error?.message || 'Failed to generate quiz.';
    const status = message.includes('Could not reach Python service') ? 502 : 500;
    res.status(status).json({ error: message });
  }
});

router.post('/upload-quiz', upload.single('file'), async (req, res) => {
  try {
    const file = req.file;
    if (!file) return res.status(400).json({ error: 'No file uploaded.' });

    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowed.includes(file.mimetype)) {
      return res.status(400).json({ error: 'Unsupported file type. Only PDF, DOCX and TXT are allowed.' });
    }

    const { quiz_type, num_questions, summarize_first, summary_length, language } = req.body;
    const limit = Number(num_questions) || 5;
    const questionCount = Math.max(1, Math.min(50, limit));

    const payload = {
      file,
      quiz_type: quiz_type || 'mcq',
      num_questions: questionCount,
      summarize_first: summarize_first === 'true' || summarize_first === true,
      summary_length: summary_length ? Number(summary_length) : null,
      lang: language || 'vi',
    };

    const response = await pythonBridge.uploadQuiz(payload);
    res.json(response);
  } catch (error) {
    console.error('[Backend] Upload-quiz error:', error?.message || error);
    const message = error?.message || 'Failed to upload file and generate quiz.';
    const status = message.includes('Could not reach Python service') ? 502 : 500;
    res.status(status).json({ error: message });
  }
});

module.exports = router;
// no additional endpoints
