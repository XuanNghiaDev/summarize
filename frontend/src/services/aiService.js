import { aiAPI } from './aiAPI';

export const summarizeText = async ({ text, model, lang, summary_length }) => {
  const response = await aiAPI.post('/summarize', { text, model, lang, summary_length });
  return response.data;
};

export const uploadDocument = async (file, { model, lang, summary_length }) => {
  const formData = new FormData();
  formData.append('document', file);
  formData.append('model', model);
  formData.append('lang', lang);
  formData.append('summary_length', String(summary_length));

  const response = await aiAPI.post('/upload', formData);

  return response.data;
};

export const generateQuiz = async ({ text, quiz_type, num_questions, lang, difficulty }) => {
  const response = await aiAPI.post('/generate-quiz', {
    text,
    quiz_type,
    num_questions,
    lang,
    difficulty,
  });

  return response.data;
};

export const uploadQuizFile = async (file, { quiz_type, num_questions, summarize_first, summary_length, language }) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('quiz_type', quiz_type);
  formData.append('num_questions', String(num_questions));
  formData.append('summarize_first', String(!!summarize_first));
  if (summary_length !== undefined && summary_length !== null) {
    formData.append('summary_length', String(summary_length));
  }
  formData.append('language', language);

  const response = await aiAPI.post('/upload-quiz', formData);

  return response.data;
};
