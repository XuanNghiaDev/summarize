const axios = require('axios');
require('dotenv').config();

const pythonUrl = process.env.PYTHON_SERVICE_URL || 'http://localhost:5000';
const client = axios.create({ baseURL: pythonUrl, timeout: 20000 });

async function summarize(payload) {
  try {
    const response = await client.post('/summarize', payload);
    return response.data;
  } catch (error) {
    if (error.response) {
      const message = error.response.data?.error || `Python service error ${error.response.status}`;
      throw new Error(message);
    }
    if (error.request) {
      throw new Error(`Could not reach Python service at ${pythonUrl}`);
    }
    throw error;
  }
}

async function generateQuiz(payload) {
  try {
    const response = await client.post('/generate-quiz', payload);
    return response.data;
  } catch (error) {
    if (error.response) {
      const message = error.response.data?.error || `Python service error ${error.response.status}`;
      throw new Error(message);
    }
    if (error.request) {
      throw new Error(`Could not reach Python service at ${pythonUrl}`);
    }
    throw error;
  }
}

async function uploadQuiz({ file, quiz_type, num_questions, summarize_first, summary_length, lang }) {
  try {
    const FormData = require('form-data');
    const form = new FormData();
    form.append('file', file.buffer, { filename: file.originalname, contentType: file.mimetype });
    form.append('quiz_type', quiz_type || 'mcq');
    form.append('num_questions', String(num_questions || 5));
    form.append('summarize_first', summarize_first ? 'true' : 'false');
    if (summary_length !== undefined && summary_length !== null) form.append('summary_length', String(summary_length));
    form.append('language', lang || 'vi');

    const headers = form.getHeaders();
    const response = await client.post('/upload-quiz', form, { headers });
    return response.data;
  } catch (error) {
    if (error.response) {
      const message = error.response.data?.error || `Python service error ${error.response.status}`;
      throw new Error(message);
    }
    if (error.request) {
      throw new Error(`Could not reach Python service at ${pythonUrl}`);
    }
    throw error;
  }
}

module.exports = { summarize, generateQuiz, uploadQuiz };
