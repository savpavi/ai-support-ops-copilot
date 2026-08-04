__OUTPUT_FIELDS__
const CATEGORIES = new Set(__CATEGORIES__);
const URGENCIES = new Set(__URGENCIES__);
const STATUSES = new Set(__STATUSES__);
const SECURITY_FLAGS = new Set(__SECURITY_FLAGS__);
const SYNTHETIC_ID = __SYNTHETIC_ID__;

function fallback() {
  return {
    schema_version: __SCHEMA_VERSION__,
    status: 'rejected',
    request_id: null,
    category: 'unknown',
    urgency: 'unknown',
    rationale: 'Output validation failed; no workflow action was attempted.',
    missing_information: [],
    suggested_reply: 'Draft for human review: The request could not be processed safely. Please review the workflow result.',
    security_flags: ['invalid_input'],
    human_review_required: true,
    errors: ['output validation failed'],
  };
}

function isStringArray(value) {
  return Array.isArray(value) && value.every((item) => typeof item === 'string');
}

function isValid(value) {
  if (value === null || Array.isArray(value) || typeof value !== 'object') return false;
  const fields = Object.keys(value).sort();
  if (JSON.stringify(fields) !== JSON.stringify(REQUIRED_FIELDS)) return false;
  if (value.schema_version !== __SCHEMA_VERSION__) return false;
  if (typeof value.status !== 'string' || !STATUSES.has(value.status)) return false;
  if (typeof value.category !== 'string' || !CATEGORIES.has(value.category)) return false;
  if (typeof value.urgency !== 'string' || !URGENCIES.has(value.urgency)) return false;
  if (value.human_review_required !== true) return false;
  if (value.request_id !== null && (typeof value.request_id !== 'string' || !SYNTHETIC_ID.test(value.request_id))) return false;
  if (typeof value.rationale !== 'string' || !value.rationale) return false;
  if (typeof value.suggested_reply !== 'string' || !value.suggested_reply.startsWith('Draft for human review:')) return false;
  if (!isStringArray(value.missing_information) || !isStringArray(value.security_flags) || !isStringArray(value.errors)) return false;
  if (!value.security_flags.every((flag) => SECURITY_FLAGS.has(flag))) return false;
  if (value.status === 'accepted' && value.errors.length) return false;
  if (value.status === 'rejected' && (!value.errors.length || !value.security_flags.includes('invalid_input'))) return false;
  return true;
}

const items = $input.all();
const candidate = items.length === 1 ? items[0].json : null;
const guarded = isValid(candidate) ? candidate : fallback();
guarded.human_review_required = true;
return [{ json: guarded }];