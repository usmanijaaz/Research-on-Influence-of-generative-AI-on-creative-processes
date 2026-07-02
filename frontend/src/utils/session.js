import { v4 as uuidv4 } from "uuid";

export function getSessionId(role) {
  const key = `session_id_${role}`;

  let sessionId = localStorage.getItem(key);
  
  if (!sessionId) {
    sessionId = uuidv4();
    localStorage.setItem(key, sessionId);
  }

  return sessionId;
}