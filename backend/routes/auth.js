const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const router = express.Router();
const DB_PATH = path.join(__dirname, '..', 'users.json');
const ACCESS_TOKEN_TTL = 1000 * 60 * 60; // 1 hour
const REFRESH_TOKEN_TTL = 1000 * 60 * 60 * 24 * 30; // 30 days

function ensureDb() {
  if (!fs.existsSync(DB_PATH)) {
    fs.writeFileSync(DB_PATH, JSON.stringify({ users: [], sessions: [] }, null, 2));
  }
}

function readDb() {
  ensureDb();
  return JSON.parse(fs.readFileSync(DB_PATH, 'utf-8'));
}

function writeDb(db) {
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
}

function hashPassword(password, salt) {
  return crypto.scryptSync(password, salt, 64).toString('hex');
}

function generateToken() {
  return crypto.randomBytes(32).toString('hex');
}

function createSession(userId) {
  const access_token = generateToken();
  const refresh_token = generateToken();
  const now = Date.now();
  return {
    user_id: userId,
    access_token,
    refresh_token,
    access_expires_at: now + ACCESS_TOKEN_TTL,
    refresh_expires_at: now + REFRESH_TOKEN_TTL,
    created_at: now,
  };
}

function formatUser(user) {
  return {
    id: user.id,
    email: user.email,
    full_name: user.full_name,
  };
}

function getSessionByAccessToken(db, token) {
  return db.sessions.find((session) => session.access_token === token && session.access_expires_at > Date.now());
}

function getSessionByRefreshToken(db, token) {
  return db.sessions.find((session) => session.refresh_token === token && session.refresh_expires_at > Date.now());
}

function getUserFromAccessToken(token) {
  const db = readDb();
  const session = getSessionByAccessToken(db, token);
  if (!session) return null;
  return db.users.find((user) => user.id === session.user_id) || null;
}

function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ detail: 'Authorization header missing or invalid.' });
  }

  const token = authHeader.split(' ')[1];
  const db = readDb();
  const session = getSessionByAccessToken(db, token);
  if (!session) {
    return res.status(401).json({ detail: 'Invalid or expired access token.' });
  }

  const user = db.users.find((u) => u.id === session.user_id);
  if (!user) {
    return res.status(401).json({ detail: 'Invalid session user.' });
  }

  req.user = user;
  req.session = session;
  next();
}

router.post('/auth/register', (req, res) => {
  const { email, password, full_name } = req.body;
  if (!email || !password) {
    return res.status(400).json({ detail: 'Email and password are required.' });
  }
  if (typeof password !== 'string' || password.length < 8) {
    return res.status(400).json({ detail: 'Password must be at least 8 characters long.' });
  }
  const normalizedEmail = String(email).trim().toLowerCase();
  const db = readDb();

  if (db.users.some((user) => user.email === normalizedEmail)) {
    return res.status(400).json({ detail: 'Email is already registered.' });
  }

  const userId = db.users.length ? Math.max(...db.users.map((user) => user.id)) + 1 : 1;
  const salt = crypto.randomBytes(16).toString('hex');
  const password_hash = hashPassword(password, salt);

  const user = {
    id: userId,
    email: normalizedEmail,
    full_name: full_name ? String(full_name).trim() : '',
    password_hash,
    password_salt: salt,
    created_at: Date.now(),
  };
  db.users.push(user);

  const session = createSession(userId);
  db.sessions.push(session);
  writeDb(db);

  return res.status(201).json({ access_token: session.access_token, refresh_token: session.refresh_token });
});

router.post('/auth/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ detail: 'Email and password are required.' });
  }

  const normalizedEmail = String(email).trim().toLowerCase();
  const db = readDb();
  const user = db.users.find((u) => u.email === normalizedEmail);
  if (!user) {
    return res.status(401).json({ detail: 'Invalid email or password.' });
  }

  const expectedHash = hashPassword(password, user.password_salt);
  if (expectedHash !== user.password_hash) {
    return res.status(401).json({ detail: 'Invalid email or password.' });
  }

  const session = createSession(user.id);
  db.sessions.push(session);
  writeDb(db);

  return res.json({ access_token: session.access_token, refresh_token: session.refresh_token });
});

router.post('/auth/logout', requireAuth, (req, res) => {
  const db = readDb();
  db.sessions = db.sessions.filter((session) => session.access_token !== req.session.access_token);
  writeDb(db);
  return res.json({ message: 'Logged out successfully.' });
});

router.post('/auth/refresh', (req, res) => {
  const { refresh_token } = req.body;
  if (!refresh_token) {
    return res.status(400).json({ detail: 'Refresh token is required.' });
  }

  const db = readDb();
  const session = getSessionByRefreshToken(db, refresh_token);
  if (!session) {
    return res.status(401).json({ detail: 'Invalid or expired refresh token.' });
  }

  db.sessions = db.sessions.filter((existing) => existing.refresh_token !== refresh_token);
  const newSession = createSession(session.user_id);
  db.sessions.push(newSession);
  writeDb(db);

  return res.json({ access_token: newSession.access_token, refresh_token: newSession.refresh_token });
});

router.get('/user/profile', requireAuth, (req, res) => {
  return res.json(formatUser(req.user));
});

router.put('/user/profile', requireAuth, (req, res) => {
  const { full_name } = req.body;
  if (full_name !== undefined && typeof full_name !== 'string') {
    return res.status(400).json({ detail: 'full_name must be a string.' });
  }

  const db = readDb();
  const user = db.users.find((u) => u.id === req.user.id);
  if (!user) {
    return res.status(404).json({ detail: 'User not found.' });
  }

  user.full_name = full_name !== undefined ? String(full_name).trim() : user.full_name;
  writeDb(db);

  return res.json(formatUser(user));
});

module.exports = router;
