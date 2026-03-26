import data from '../data/scored_senators.json';
import scripts from '../data/call_scripts.json';

/** Full ranked array of senator objects. */
export const senators = data.senators;

// O(1) lookup indexes built once at module load
const bySlug = new Map(senators.map((s) => [s.slug, s]));

const byState = new Map();
for (const s of senators) {
  const list = byState.get(s.state) || [];
  list.push(s);
  byState.set(s.state, list);
}

/** Return a single senator by slug, or undefined. */
export function getBySlug(slug) {
  return bySlug.get(slug);
}

/** Return all senators for a state code (empty array if none). */
export function getByState(stateCode) {
  return byState.get(stateCode) || [];
}

/** Return personalized call script if available, otherwise the generic template. */
export function getScript(slug) {
  return scripts[slug] || scripts.generic;
}

/** Alias -- returns the full sorted array. */
export function allSenators() {
  return senators;
}
