/**
 * Slugify a senator's name + state to match the Python build script.
 * e.g. slugify("Susan Collins", "ME") => "susan-collins-me"
 */
export function slugify(name, state) {
  return (
    name
      .toLowerCase()
      .replace(/[^a-z\s-]/g, '')
      .replace(/\s+/g, '-') +
    '-' +
    state.toLowerCase()
  );
}
