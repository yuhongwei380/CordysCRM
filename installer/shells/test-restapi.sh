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

log "=========================================="
log "CordysCRM REST API Test Script"
log "=========================================="
log "BASE_URL=${BASE_URL} user=${USERNAME} org=${ORG_ID}"
log "=========================================="
echo

# ==========================================
# 1. Basic Health Check
# ==========================================
log "[1/20] Basic Health Check"

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
log "System version payload:"
pretty_print "$(curl -k -u "${USERNAME}:${PASSWORD}" -s "${BASE_URL}/system/version")"
echo

# 4) Locale language change
json_post "/locale-language/change" '{"language":"zh_CN"}' "Locale language change"

echo

# ==========================================
# 2. Home Statistics
# ==========================================
log "[2/20] Home Statistics"

json_post "/home/statistic/lead" '{}' "Home lead statistics"
json_post "/home/statistic/opportunity" '{}' "Home opportunity statistics"
json_post "/home/statistic/opportunity/underway" '{}' "Home underway opportunity statistics"
json_post "/home/statistic/opportunity/success" '{}' "Home success opportunity statistics"
json_get "/home/statistic/department/tree" "Home department tree"

echo

# ==========================================
# 3. Dashboard Module
# ==========================================
log "[3/20] Dashboard Module"

json_get "/dashboard/module/tree" "Dashboard module tree"
json_get "/dashboard/module/count" "Dashboard module count"

echo

# ==========================================
# 4. Customer Module
# ==========================================
log "[4/20] Customer Module"

json_get "/account/module/form" "Customer form config"
json_post "/account/page" '{"current":1,"pageSize":1}' "Customer page"
json_post "/account/option" '{"current":1,"pageSize":10,"keyword":""}' "Customer options"
json_get "/account/tab" "Customer tab config"

json_post "/account/contact/page" '{"current":1,"pageSize":1}' "Customer contact page"
json_get "/account/contact/module/form" "Customer contact form config"
json_get "/account/contact/tab" "Customer contact tab"

json_post "/account/follow/record/page" '{"current":1,"pageSize":1}' "Customer follow record page"
json_post "/account/follow/plan/page" '{"current":1,"pageSize":1}' "Customer follow plan page"

json_post "/account/contract/page" '{"current":1,"pageSize":1}' "Customer contract page"
json_post "/account/contract/payment-plan/page" '{"current":1,"pageSize":1}' "Customer contract payment plan page"
json_post "/account/contract/payment-record/page" '{"current":1,"pageSize":1}' "Customer contract payment record page"
json_post "/account/invoice/page" '{"current":1,"pageSize":1}' "Customer invoice page"

echo

# ==========================================
# 5. Customer Pool Module
# ==========================================
log "[5/20] Customer Pool Module"

json_post "/account-pool/page" '{"current":1,"pageSize":1}' "Customer pool page"
json_post "/pool/account/page" '{"current":1,"pageSize":1}' "Pool customer page"
json_get "/pool/account/options" "Pool customer options"

echo

# ==========================================
# 6. Clue (Lead) Module
# ==========================================
log "[6/20] Clue (Lead) Module"

json_get "/lead/module/form" "Clue form config"
json_post "/lead/page" '{"current":1,"pageSize":1}' "Clue page"
json_get "/lead/tab" "Clue tab config"

json_post "/lead/follow/record/page" '{"current":1,"pageSize":1}' "Clue follow record page"
json_post "/lead/follow/plan/page" '{"current":1,"pageSize":1}' "Clue follow plan page"

json_post "/lead-pool/page" '{"current":1,"pageSize":1}' "Clue pool page"
json_post "/pool/lead/page" '{"current":1,"pageSize":1}' "Pool lead page"
json_get "/pool/lead/options" "Pool lead options"

echo

# ==========================================
# 7. Opportunity Module
# ==========================================
log "[7/20] Opportunity Module"

json_get "/opportunity/module/form" "Opportunity form config"
json_post "/opportunity/page" '{"current":1,"pageSize":1}' "Opportunity page"
json_post "/opportunity/statistic" '{"viewId":"ALL"}' "Opportunity statistic"
json_get "/opportunity/tab" "Opportunity tab config"

json_post "/opportunity/follow/record/page" '{"current":1,"pageSize":1}' "Opportunity follow record page"
json_post "/opportunity/follow/plan/page" '{"current":1,"pageSize":1}' "Opportunity follow plan page"

json_get "/opportunity/stage/get" "Opportunity stage config"

echo

# ==========================================
# 8. Product Module
# ==========================================
log "[8/20] Product Module"

json_get "/product/module/form" "Product form config"
json_post "/product/page" '{"current":1,"pageSize":1}' "Product page"
json_get "/product/list/option" "Product options"

json_post "/price/page" '{"current":1,"pageSize":1}' "Price page"
json_get "/price/module/form" "Price form config"

echo

# ==========================================
# 9. Contract Module
# ==========================================
log "[9/20] Contract Module"

json_get "/contract/module/form" "Contract form config"
json_post "/contract/page" '{"current":1,"pageSize":1}' "Contract page"
json_get "/contract/tab" "Contract tab config"

json_post "/contract/payment-plan/page" '{"current":1,"pageSize":1}' "Contract payment plan page"
json_get "/contract/payment-plan/module/form" "Payment plan form config"
json_get "/contract/payment-plan/tab" "Payment plan tab"

json_post "/contract/payment-record/page" '{"current":1,"pageSize":1}' "Contract payment record page"
json_get "/contract/payment-record/module/form" "Payment record form config"
json_get "/contract/payment-record/tab" "Payment record tab"

json_post "/contract/business-title/page" '{"current":1,"pageSize":1}' "Business title page"

echo

# ==========================================
# 10. Invoice Module
# ==========================================
log "[10/20] Invoice Module"

json_post "/invoice/page" '{"current":1,"pageSize":1}' "Invoice page"
json_get "/invoice/module/form" "Invoice form config"
json_get "/invoice/tab" "Invoice tab"

echo

# ==========================================
# 11. View Management
# ==========================================
log "[11/20] View Management"

json_get "/account/view/list" "Customer view list"
json_get "/account/contact/view/list" "Customer contact view list"
json_get "/pool/account/view/list" "Pool customer view list"

json_get "/lead/view/list" "Clue view list"
json_get "/pool/lead/view/list" "Pool lead view list"

json_get "/opportunity/view/list" "Opportunity view list"

json_get "/contract/view/list" "Contract view list"
json_get "/contract/payment-plan/view/list" "Payment plan view list"
json_get "/contract/payment-record/view/list" "Payment record view list"
json_get "/invoice/view/list" "Invoice view list"

echo

# ==========================================
# 12. Search Module
# ==========================================
log "[12/20] Search Module"

json_post "/global/search/account" '{"current":1,"pageSize":1,"keyword":""}' "Global search customer"
json_post "/global/search/customer_pool" '{"current":1,"pageSize":1,"keyword":""}' "Global search customer pool"
json_post "/global/search/contact" '{"current":1,"pageSize":1,"keyword":""}' "Global search contact"
json_post "/global/search/lead" '{"current":1,"pageSize":1,"keyword":""}' "Global search lead"
json_post "/global/search/clue_pool" '{"current":1,"pageSize":1,"keyword":""}' "Global search clue pool"
json_post "/global/search/opportunity" '{"current":1,"pageSize":1,"keyword":""}' "Global search opportunity"

json_post "/advanced/search/account" '{"current":1,"pageSize":1}' "Advanced search customer"
json_post "/advanced/search/account-pool" '{"current":1,"pageSize":1}' "Advanced search customer pool"
json_post "/advanced/search/contact" '{"current":1,"pageSize":1}' "Advanced search contact"
json_post "/advanced/search/lead" '{"current":1,"pageSize":1}' "Advanced search lead"
json_post "/advanced/search/lead-pool" '{"current":1,"pageSize":1}' "Advanced search lead pool"
json_post "/advanced/search/opportunity" '{"current":1,"pageSize":1}' "Advanced search opportunity"

json_get "/global/search/module/count" "Global search module count"

echo

# ==========================================
# 13. Follow Up Module
# ==========================================
log "[13/20] Follow Up Module"

json_post "/follow/record/page" '{"current":1,"pageSize":1}' "Follow record page"
json_get "/follow/record/tab" "Follow record tab"

json_post "/follow/plan/page" '{"current":1,"pageSize":1}' "Follow plan page"
json_get "/follow/plan/tab" "Follow plan tab"

json_get "/follow/record/view/list" "Follow record view list"
json_get "/follow/plan/view/list" "Follow plan view list"

echo

# ==========================================
# 14. System Module
# ==========================================
log "[14/20] System Module"

json_get "/module/list" "Module list"
json_get "/module/user/dept/tree" "Module user dept tree"
json_get "/module/role/tree" "Module role tree"
json_get "/module/advanced-search/settings" "Module advanced search settings"

json_get "/dict/get/ACCOUNT" "Dict get (account)"
json_get "/dict/config" "Dict config"

json_get "/search/config/get" "Search config"
json_get "/mask/config/get" "Mask config"

json_get "/navigation/list" "Navigation list"

echo

# ==========================================
# 15. Organization Module
# ==========================================
log "[15/20] Organization Module"

json_get "/department/tree" "Department tree"

echo

# ==========================================
# 16. Role & Permission Module
# ==========================================
log "[16/20] Role & Permission Module"

json_get "/role/list" "Role list"
json_get "/role/user/dept/tree" "Role user dept tree"
json_get "/role/dept/tree" "Role dept tree"

echo

# ==========================================
# 17. Message & Notification Module
# ==========================================
log "[17/20] Message & Notification Module"

json_post "/notification/list/all/page" '{"current":1,"pageSize":10}' "Notification list"
json_get "/notification/count" "Notification count"

echo

# ==========================================
# 18. Personal Center Module
# ==========================================
log "[18/20] Personal Center Module"

json_get "/personal/center/info" "Personal center info"
json_post "/personal/center/follow/plan/list" '{"current":1,"pageSize":10}' "Personal follow plan list"

json_post "/export/center/list" '{"current":1,"pageSize":10}' "Export center list"

json_get "/user/api/key/list" "API key list"

echo

# ==========================================
# 19. File Management Module
# ==========================================
log "[19/20] File Management Module"

json_post "/pic/upload/temp" '{}' "Upload temp pic (empty test)"
json_post "/attachment/upload/temp" '{}' "Upload temp attachment (empty test)"

echo

# ==========================================
# 20. Agent Module
# ==========================================
log "[20/20] Agent Module"

json_post "/agent/page" '{"current":1,"pageSize":10}' "Agent page"
json_get "/agent/option" "Agent options"
json_get "/agent/module/tree" "Agent module tree"
json_get "/agent/module/count" "Agent module count"

echo

# ==========================================
# Summary
# ==========================================
log "=========================================="
log "REST API Test Completed Successfully!"
log "=========================================="
log "All 20 test modules passed:"
log "  [1/20]  Basic Health Check"
log "  [2/20]  Home Statistics"
log "  [3/20]  Dashboard Module"
log "  [4/20]  Customer Module"
log "  [5/20]  Customer Pool Module"
log "  [6/20]  Clue (Lead) Module"
log "  [7/20]  Opportunity Module"
log "  [8/20]  Product Module"
log "  [9/20]  Contract Module"
log "  [10/20] Invoice Module"
log "  [11/20] View Management"
log "  [12/20] Search Module"
log "  [13/20] Follow Up Module"
log "  [14/20] System Module"
log "  [15/20] Organization Module"
log "  [16/20] Role & Permission Module"
log "  [17/20] Message & Notification Module"
log "  [18/20] Personal Center Module"
log "  [19/20] File Management Module"
log "  [20/20] Agent Module"
log "=========================================="
