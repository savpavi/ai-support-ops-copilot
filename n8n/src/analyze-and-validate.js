const SCHEMA_VERSION = __SCHEMA_VERSION__;
const MAX_MESSAGE_LENGTH = __MAX_MESSAGE_LENGTH__;
const SYNTHETIC_ID = __SYNTHETIC_ID__;
const URL_PATTERN = __URL_PATTERN__;
const CREDENTIAL_REQUEST_PATTERN = __CREDENTIAL_PATTERN__;
const URGENT_PATTERN = __URGENT_PATTERN__;

__CATEGORY_RULES__

__PROMPT_INJECTION_PATTERNS__

const escapeTerm = (term) => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const containsAny = (text, terms) => terms.some((term) => new RegExp(`\\b${escapeTerm(term)}\\b`).test(text));

function validateInput(value) {
  if (value === null || Array.isArray(value) || typeof value !== 'object') {
    return ['input must be a JSON object'];
  }

  const errors = [];
  const allowedKeys = new Set(['request_id', 'message']);
  const extraKeys = Object.keys(value).filter((key) => !allowedKeys.has(key)).sort();
  if (extraKeys.length) {
    errors.push(`unexpected fields: ${extraKeys.join(', ')}`);
  }

  if (typeof value.request_id !== 'string' || !SYNTHETIC_ID.test(value.request_id)) {
    errors.push('request_id must match SYN-[A-Z0-9-] and be 7-44 characters long');
  }

  if (typeof value.message !== 'string') {
    errors.push('message must be a string');
  } else if (!value.message.trim()) {
    errors.push('message must not be empty');
  } else if ([...value.message].length > MAX_MESSAGE_LENGTH) {
    errors.push(`message must be at most ${MAX_MESSAGE_LENGTH} characters`);
  }

  return errors;
}

function securityFlags(text) {
  const flags = [];
  if (PROMPT_INJECTION_PATTERNS.some((pattern) => pattern.test(text))) flags.push('prompt_injection');
  if (CREDENTIAL_REQUEST_PATTERN.test(text)) flags.push('credential_request');
  if (containsAny(text, __PAYMENT_TERMS__)) flags.push('payment_data');
  if (containsAny(text, __IDENTITY_TERMS__)) flags.push('sensitive_identity_data');
  if (URL_PATTERN.test(text)) flags.push('suspicious_link');
  return flags.sort();
}

function classifyCategory(text) {
  for (const [category, terms] of CATEGORY_RULES) {
    if (containsAny(text, terms)) return category;
  }
  return 'general';
}

function classifyUrgency(text, flags) {
  if (containsAny(text, __CRITICAL_TERMS__)) return 'critical';
  if (URGENT_PATTERN.test(text) || containsAny(text, __HIGH_TERMS__)) return 'high';
  if (flags.length) return 'high';
  if (containsAny(text, __LOW_TERMS__)) return 'low';
  return 'normal';
}

function missingInformation(category, text) {
  const missing = [];
  if (category === 'access_issue') {
    if (!containsAny(text, __MI_access_issue_0_TERMS__)) missing.push(__MI_access_issue_0_LABEL__);
    if (!containsAny(text, __MI_access_issue_1_TERMS__)) missing.push(__MI_access_issue_1_LABEL__);
  } else if (category === 'billing') {
    if (!containsAny(text, __MI_billing_0_TERMS__)) missing.push(__MI_billing_0_LABEL__);
    if (!containsAny(text, __MI_billing_1_TERMS__)) missing.push(__MI_billing_1_LABEL__);
  } else if (category === 'service_disruption') {
    if (!containsAny(text, __MI_service_disruption_0_TERMS__)) missing.push(__MI_service_disruption_0_LABEL__);
    if (!containsAny(text, __MI_service_disruption_1_TERMS__)) missing.push(__MI_service_disruption_1_LABEL__);
  } else if (category === 'account_change') {
    if (!containsAny(text, __MI_account_change_0_TERMS__)) missing.push(__MI_account_change_0_LABEL__);
  } else if (text.split(/\s+/).filter(Boolean).length < __MI_GENERAL_MIN_WORDS__ || containsAny(text, __MI_GENERAL_TERMS__)) {
    missing.push(__MI_GENERAL_LABEL__);
  }
  return missing;
}

function rationale(category, urgency, flags) {
  const categoryReasons = {
    access_issue: 'The request describes a sign-in or access problem.',
    account_change: 'The request asks for an account or profile change.',
    billing: 'The request concerns a charge, payment, invoice, or refund.',
    service_disruption: 'The request describes unavailable or failing service.',
    general: 'The request lacks a more specific supported category.',
  };
  const urgencyReasons = {
    low: 'It explicitly indicates that no prompt response is needed.',
    normal: 'No deterministic high-urgency indicator was found.',
    high: 'Urgent access, disruption, or security-review indicators were found.',
    critical: 'The text contains an explicit safety or medical emergency indicator.',
  };
  const securityReason = flags.length ? ' Security-sensitive content requires review.' : '';
  return `${categoryReasons[category]} ${urgencyReasons[urgency]}${securityReason}`;
}

function suggestedReply(category, missing, flags) {
  const opening = flags.length
    ? 'Draft for human review: We received your request, but it contains content that requires a security review.'
    : `Draft for human review: We received your ${category.replaceAll('_', ' ')} request.`;
  if (missing.length) {
    return `${opening} Please provide: ${missing.join(', ')}. Do not include passwords, payment-card data, or identity documents.`;
  }
  return `${opening} A support operator will review the details before any action is taken.`;
}

function securityText(value) {
  if (value === null || Array.isArray(value) || typeof value !== 'object') return '';
  return ['message', 'request_text']
    .map((field) => value[field])
    .filter((part) => typeof part === 'string')
    .map((part) => part.trim().toLowerCase())
    .join('\n');
}

function rejectedResult(value, errors, detectedFlags) {
  const requestId = value !== null && !Array.isArray(value) && typeof value === 'object'
    && typeof value.request_id === 'string' && SYNTHETIC_ID.test(value.request_id)
    ? value.request_id
    : null;
  return {
    schema_version: SCHEMA_VERSION,
    status: 'rejected',
    request_id: requestId,
    category: 'unknown',
    urgency: 'unknown',
    rationale: 'Input validation failed; no classification was attempted.',
    missing_information: [],
    suggested_reply: 'Draft for human review: The request could not be processed safely. Please provide a valid synthetic request.',
    security_flags: [...new Set(['invalid_input', ...detectedFlags])].sort(),
    human_review_required: true,
    errors,
  };
}

const input = $input.first().json;
const errors = validateInput(input);
if (errors.length) {
  return [{ json: rejectedResult(input, errors, securityFlags(securityText(input))) }];
}

const text = input.message.trim().toLowerCase();
const flags = securityFlags(text);
const category = classifyCategory(text);
const urgency = classifyUrgency(text, flags);
const missing = missingInformation(category, text);

return [{
  json: {
    schema_version: SCHEMA_VERSION,
    status: 'accepted',
    request_id: input.request_id,
    category,
    urgency,
    rationale: rationale(category, urgency, flags),
    missing_information: missing,
    suggested_reply: suggestedReply(category, missing, flags),
    security_flags: flags,
    human_review_required: true,
    errors: [],
  },
}];