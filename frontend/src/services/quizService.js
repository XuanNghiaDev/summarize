import { aiAPI } from './aiAPI';

export const generateQuiz = (data) =>
  aiAPI.post('/generate-quiz', data).then((response) => response.data);
