#!/usr/bin/env bash
set -euo pipefail

# Basic auth and target service
BASE_URL="${BASE_URL:-http://127.0.0.1:8081}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-CordysCRM}"
ORG_ID="${ORG_ID:-100001}"
JQ_BIN="$(command -v jq || true)"

log() {
  printf '[INFO] %s\n' "$*"
}

fail() {
  printf '[ERROR] %s\n' "$*" >&2
  exit 1
}

json_get() {
  local path="$1" desc="$2"
  local resp code payload
  resp=$(curl -k -u "${USERNAME}:${PASSWORD}" \
    -H "Organization-Id: ${ORG_ID}" \
    -s -w 'HTTPSTATUS:%{http_code}' \
    "${BASE_URL}${path}") || fail "request failed: ${desc}"
  code="${resp##*HTTPSTATUS:}"
  payload="${resp%HTTPSTATUS:*}"
  if [[ "${code}" != "200" ]]; then
    fail "${desc} http ${code} (expected 200)"
  fi
  if [[ -z "${payload// }" ]]; then
    log "${desc} OK but payload empty"
  else
    log "${desc} OK (${code}), payload:"
    pretty_print "${payload}"
  fi
  echo
}

pretty_print() {
  local payload="$1"
  if [[ -n "${JQ_BIN}" ]]; then
    echo "${payload}" | "${JQ_BIN}" .
  else
    echo "${payload}"
  fi
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

json_post() {
  local path="$1" body="$2" desc="$3"
  local resp code payload
  resp=$(curl -k -u "${USERNAME}:${PASSWORD}" \
    -H "Content-Type: application/json" \
    -H "Organization-Id: ${ORG_ID}" \
    -s -w 'HTTPSTATUS:%{http_code}' \
    -d "${body}" \
    "${BASE_URL}${path}") || fail "request failed: ${desc}"
  code="${resp##*HTTPSTATUS:}"
  payload="${resp%HTTPSTATUS:*}"
  if [[ "${code}" != "200" ]]; then
    fail "${desc} http ${code} (expected 200)"
  fi
  if [[ -z "${payload// }" ]]; then
    log "${desc} OK but payload empty"
  else
    log "${desc} OK (${code}), payload:"
    pretty_print "${payload}"
  fi
  echo
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

# 3) System version endpoint + payload
check_endpoint "/system/version" 200 "System version"
log "System version payload:"
pretty_print "$(curl -k -u "${USERNAME}:${PASSWORD}" -s "${BASE_URL}/system/version")"
echo

# 4) Home statistics (empty payload uses defaults) + payload
json_post "/home/statistic/lead" '{}' "Home lead statistics"
json_post "/home/statistic/opportunity" '{}' "Home opportunity statistics"
json_post "/home/statistic/opportunity/success" '{}' "Home success opportunity statistics"
json_get "/home/statistic/department/tree" "Home department tree"

# 5) Dashboard module tree/count
json_get "/dashboard/module/tree" "Dashboard module tree"
json_get "/dashboard/module/count" "Dashboard module count"

# 6) Opportunity page data (pageSize=1) + payload
json_post "/opportunity/page" '{"current":1,"pageSize":1}' "Opportunity page"

# 7) Contract list (pageSize=1)
json_post "/contract/page" '{"current":1,"pageSize":1}' "Contract page"

# 8) Contract payment plan (pageSize=1)
json_post "/contract/payment-plan/page" '{"current":1,"pageSize":1}' "Contract payment plan page"

# 9) Contract payment record (pageSize=1)
json_post "/contract/payment-record/page" '{"current":1,"pageSize":1}' "Contract payment record page"

# 10) Contract invoice (pageSize=1)
json_post "/invoice/page" '{"current":1,"pageSize":1}' "Invoice page"

log "REST API smoke test done"
