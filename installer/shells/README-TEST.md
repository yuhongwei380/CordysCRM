# CordysCRM REST API Test Scripts

This directory contains test scripts for testing CordysCRM REST API endpoints.

## Overview

There are two test scripts available:

1. **`test-restapi.sh`** - Bash-based test script (lightweight, no dependencies)
2. **`test-restapi.py`** - Python-based test script (feature-rich, detailed reporting)

## Quick Start

### Using Bash Script

```bash
# Run with default settings
./test-restapi.sh

# Run with custom settings
BASE_URL=http://localhost:8081 \
USERNAME=admin \
PASSWORD=CordysCRM \
ORG_ID=100001 \
./test-restapi.sh
```

### Using Python Script

```bash
# Install dependencies (first time only)
pip install requests

# Run with default settings
python3 test-restapi.py

# Run with custom settings
python3 test-restapi.py \
  --base-url http://localhost:8081 \
  --username admin \
  --password CordysCRM \
  --org-id 100001

# Run with verbose output
python3 test-restapi.py --verbose

# Save results to JSON file
python3 test-restapi.py --output test-results.json
```

## Configuration

### Environment Variables (Bash Script)

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | Base URL of the API server | `http://127.0.0.1:8081` |
| `USERNAME` | Username for authentication | `admin` |
| `PASSWORD` | Password for authentication | `CordysCRM` |
| `ORG_ID` | Organization ID | `100001` |

### Command Line Options (Python Script)

| Option | Description | Default |
|--------|-------------|---------|
| `--base-url URL` | Base URL of the API server | `http://127.0.0.1:8081` |
| `--username USER` | Username for authentication | `admin` |
| `--password PASS` | Password for authentication | `CordysCRM` |
| `--org-id ID` | Organization ID | `100001` |
| `--timeout SEC` | Request timeout in seconds | `30` |
| `--verbose` | Enable verbose output | `false` |
| `--output FILE` | Save test results to JSON file | `none` |

## Test Coverage

The test scripts cover 20 modules with 100+ API endpoints:

### Test Modules

1. **Basic Health Check** - System health and version
2. **Home Statistics** - Dashboard statistics
3. **Dashboard Module** - Dashboard management
4. **Customer Module** - Customer CRUD and relations
5. **Customer Pool Module** - Public pool management
6. **Clue (Lead) Module** - Lead management
7. **Opportunity Module** - Business opportunity management
8. **Product Module** - Product and price management
9. **Contract Module** - Contract and payment management
10. **Invoice Module** - Invoice management
11. **View Management** - Custom views for all modules
12. **Search Module** - Global and advanced search
13. **Follow Up Module** - Follow records and plans
14. **System Module** - System configuration
15. **Organization Module** - Organization structure
16. **Role & Permission Module** - Access control
17. **Message & Notification Module** - Notification system
18. **Personal Center Module** - User settings
19. **File Management Module** - File upload/download
20. **Agent Module** - AI agent management

## Test Output

### Bash Script Output

```
[INFO] Testing GET /system/version (System version)
[INFO]   ✓ OK (200) - 15ms
[INFO] Testing POST /home/statistic/lead (Home lead statistics)
[INFO]   ✓ OK (200) - 23ms
...
[INFO] REST API Test Completed Successfully!
[INFO] All 20 test modules passed
```

### Python Script Output

```
[10:30:45] [INFO] ============================================
[10:30:45] [INFO] CordysCRM REST API Test Suite
[10:30:45] [INFO] ============================================
[10:30:45] [INFO] Base URL: http://127.0.0.1:8081
[10:30:45] [INFO] Username: admin
[10:30:45] [INFO] Organization ID: 100001
[10:30:45] [INFO] ============================================

[10:30:45] [INFO]
[10:30:45] [INFO] [1/20] Basic Health Check
[10:30:45] [INFO] ------------------------------------------------------------
[10:30:45] [INFO] Testing GET /v3/api-docs (OpenAPI docs)
[10:30:45] [INFO]   ✓ OK (200) - 12ms [SUCCESS]
[10:30:45] [INFO] Testing GET /system/version (System version)
[10:30:45] [INFO]   ✓ OK (200) - 8ms [SUCCESS]
...
[10:30:50] [INFO]
[10:30:50] [INFO] ============================================
[10:30:50] [INFO] Test Summary
[10:30:50] [INFO] ============================================
[10:30:50] [INFO] Total Tests: 150
[10:30:50] [INFO] Passed: 150
[10:30:50] [INFO] Failed: 0
[10:30:50] [INFO] Success Rate: 100.0%
[10:30:50] [INFO] ============================================
[10:30:50] [INFO] ✓ All tests passed! [SUCCESS]
[10:30:50] [INFO] ============================================
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: Failed to connect to BASE_URL
   ```
   Solution: Ensure the CordysCRM backend server is running and the BASE_URL is correct.

2. **Authentication Failed**
   ```
   Error: HTTP 401 Unauthorized
   ```
   Solution: Check that the USERNAME and PASSWORD are correct and the user has proper permissions.

3. **Timeout Errors**
   ```
   Error: Request timeout
   ```
   Solution: Increase the timeout value with `--timeout 60` (Python) or check server performance.

4. **SSL Certificate Errors**
   ```
   Error: SSL certificate problem
   ```
   Solution: The scripts use `-k` (Bash) or `verify=False` (Python) to ignore SSL warnings for testing. For production, use proper SSL certificates.

## Running Tests Programmatically

### In CI/CD Pipelines

```bash
# Example: GitHub Actions
- name: Run API Tests
  run: |
    pip install requests
    python3 installer/shells/test-restapi.py \
      --base-url ${{ secrets.API_URL }} \
      --username ${{ secrets.API_USERNAME }} \
      --password ${{ secrets.API_PASSWORD }} \
      --org-id ${{ secrets.ORG_ID }} \
      --output test-results.json

- name: Upload Test Results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-results.json
```

### As Part of Development Workflow

```bash
# Before committing changes
git checkout -b feature/new-api-endpoints

# Make changes and test
./installer/shells/test-restapi.py --verbose

# If all tests pass, commit and push
git commit -am "Add new API endpoints"
git push origin feature/new-api-endpoints
```

## Contributing

When adding new API endpoints:

1. Add the endpoint test to the appropriate module function in `test-restapi.py`
2. For Bash script, add the test call in the corresponding section
3. Update this README with the new module if needed
4. Test locally before committing

## Requirements

### Bash Script

- Bash 4.0+
- curl
- jq (optional, for pretty-printing JSON)

### Python Script

- Python 3.7+
- requests library (`pip install requests`)

## License

This test script is part of CordysCRM project.

## Support

For issues or questions about the test scripts, please refer to the main CordysCRM documentation or open an issue in the project repository.
