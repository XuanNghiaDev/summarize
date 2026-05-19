const express = require('express');
const cors = require('cors');
const summarizeRouter = require('./routes/summarize');
const authRouter = require('./routes/auth');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json({ limit: '5mb' }));

app.use((req, res, next) => {
  console.log(`[Backend] ${req.method} ${req.originalUrl}`);
  next();
});

app.use('/', authRouter);
app.use('/api', summarizeRouter);

const port = process.env.PORT || 3001;
app.listen(port, () => {
  console.log(`[Backend] Listening on http://localhost:${port}`);
});
