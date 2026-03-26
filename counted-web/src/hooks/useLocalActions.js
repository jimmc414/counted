import { useState, useCallback } from 'react';

const STORAGE_KEY = 'counted_actions';

function loadActions() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveActions(actions) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(actions));
}

/**
 * Manage a localStorage-backed list of constituent action records.
 * Each record: { senator_slug, action_type, timestamp, zip }
 */
export function useLocalActions() {
  const [actions, setActions] = useState(loadActions);

  const logAction = useCallback((senator_slug, action_type, zip) => {
    const record = { senator_slug, action_type, timestamp: new Date().toISOString(), zip };
    setActions((prev) => {
      const next = [...prev, record];
      saveActions(next);
      return next;
    });
  }, []);

  const hasContacted = useCallback(
    (senator_slug) => actions.some((a) => a.senator_slug === senator_slug),
    [actions]
  );

  const getActionCount = useCallback(() => actions.length, [actions]);

  return { actions, logAction, hasContacted, getActionCount };
}
