#!/usr/bin/env bash
set -euo pipefail

# Basic auth and target service
BASE_URL="${BASE_URL:-http://127.0.0.1:8081}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-CordysCRM}"
ORG_ID="${ORG_ID:-100001}"

log() {
  printf '[INFO] %s\n' "$*"
}

fail() {
  printf '[ERROR] %s\n' "$*" >&2
  exit 1
}

check_endpoint() {
  local path="$1" expect="$2" desc="$3"
  local code
  code=$(curl -k -u "${USERNAME}:${PASSWORD}" -s -o /dev/null -w '%{http_code}' "${BASE_URL}${path}") || fail "request failed: ${desc}"
  if [[ "${code}" != "${expect}" ]]; then
    fail "${desc} http ${code} (expected ${expect})"
  fi
  log "${desc} OK (${code})"
}

log "BASE_URL=${BASE_URL} user=${USERNAME} org=${ORG_ID}"

# 1) OpenAPI doc reachable
check_endpoint "/v3/api-docs" 200 "OpenAPI docs"

# 2) Swagger UI reachable (allow 200/302)
ui_code=$(curl -k -u "${USERNAME}:${PASSWORD}" -s -o /dev/null -w '%{http_code}' "${BASE_URL}/swagger-ui/index.html")
if [[ "${ui_code}" != "200" && "${ui_code}" != "302" ]]; then
  fail "Swagger UI http ${ui_code} (expected 200/302)"
fi
log "Swagger UI OK (${ui_code})"

# 3) System version endpoint
check_endpoint "/system/version" 200 "System version"

# 4) Opportunity page data (pageSize=1)
log "Checking opportunity page data..."
op_body='{"pageNum":1,"pageSize":1}'
op_code=$(curl -k -u "${USERNAME}:${PASSWORD}" \
  -H "Content-Type: application/json" \
  -H "Organization-Id: ${ORG_ID}" \
  -s -o /dev/null -w '%{http_code}' \
  -d "${op_body}" \
  "${BASE_URL}/opportunity/page") || fail "request failed: opportunity page"
if [[ "${op_code}" != "200" ]]; then
  fail "Opportunity page http ${op_code} (expected 200)"
fi
log "Opportunity page OK (${op_code})"

log "REST API smoke test done"
