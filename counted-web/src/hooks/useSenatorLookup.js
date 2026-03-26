import { useMemo } from 'react';
import zipToState from '../data/zip_to_state.json';
import { getByState, senators } from '../lib/senators';

const NON_VOTING = new Set(['DC', 'PR', 'GU', 'AS', 'VI', 'MP', 'MIL']);
const TOP_N = 10;

/**
 * Given a 5-digit ZIP, return the user's state, their senators,
 * and the top national targets (excluding their own senators).
 */
export function useSenatorLookup(zip) {
  return useMemo(() => {
    if (!zip || zip.length < 3) {
      return { state: null, mySenators: [], topTargets: [], noVotingSenators: false };
    }

    const prefix = zip.slice(0, 3);
    const state = zipToState[prefix] || null;

    if (!state) {
      return { state: null, mySenators: [], topTargets: [], noVotingSenators: false };
    }

    if (NON_VOTING.has(state)) {
      return { state, mySenators: [], topTargets: senators.slice(0, TOP_N), noVotingSenators: true };
    }

    const mySenators = getByState(state);
    const mySlugs = new Set(mySenators.map((s) => s.slug));
    const topTargets = senators.filter((s) => !mySlugs.has(s.slug)).slice(0, TOP_N);

    return { state, mySenators, topTargets, noVotingSenators: false };
  }, [zip]);
}
