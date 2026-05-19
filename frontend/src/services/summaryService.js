import { aiAPI } from './aiAPI';

export const summarize = (data) =>
  aiAPI.post('/summarize', data).then((response) => response.data);
