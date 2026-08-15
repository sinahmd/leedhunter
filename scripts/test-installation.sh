#!/bin/bash
# LeedHunter Installation Test Script
# Run this script after installing LeedHunter to verify everything works

set -e  # Exit on error

echo "=========================================="
echo "LeedHunter Installation Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_exit_code="${3:-0}"

    echo -n "Testing: $test_name... "

    if output=$(eval "$command" 2>&1); then
        actual_exit_code=$?
    else
        actual_exit_code=$?
    fi

    if [ $actual_exit_code -eq $expected_exit_code ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (expected exit code $expected_exit_code, got $actual_exit_code)"
        echo "  Output: $output"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test 1: Check Python version
echo "Step 1: Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
    echo -e "  Python version: ${GREEN}$PYTHON_VERSION${NC} (>= 3.10 required)"
else
    echo -e "  Python version: ${RED}$PYTHON_VERSION${NC} (>= 3.10 required)"
    echo "  Please upgrade Python to 3.10 or higher"
    exit 1
fi
echo ""

# Test 2: Check if leedhunter command exists
echo "Step 2: Checking leedhunter command..."
if command -v leedhunter &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} leedhunter command found"
else
    echo -e "  ${RED}✗${NC} leedhunter command not found"
    echo "  Please install LeedHunter: pip install -e \".[dev]\""
    exit 1
fi
echo ""

# Test 3: Version check
echo "Step 3: Running version check..."
run_test "leedhunter --version" "leedhunter --version"
echo ""

# Test 4: Help display
echo "Step 4: Running help display..."
run_test "leedhunter --help" "leedhunter --help"
echo ""

# Test 5: Doctor check
echo "Step 5: Running health check..."
run_test "leedhunter doctor" "leedhunter doctor" 0
echo ""

# Test 6: Search query
echo "Step 6: Running search query..."
run_test "leedhunter search" "leedhunter search 'auto importers in Tehran'" 0
echo ""

# Test 7: Research job
echo "Step 7: Running research job..."
run_test "leedhunter hunt" "leedhunter hunt 'Find auto importers in Tehran' --location Tehran --industry Automotive" 0
echo ""

# Test 8: Lead scoring
echo "Step 8: Running lead scoring..."
run_test "leedhunter score" "leedhunter score 'Example Automotive' --phone --email --website" 0
echo ""

# Test 9: JSON export
echo "Step 9: Running JSON export..."
run_test "leedhunter export (JSON)" "leedhunter export --format json --output /tmp/test-output.json --objective 'Find auto importers in Tehran'" 0

# Verify JSON file
if [ -f /tmp/test-output.json ]; then
    if python3 -m json.tool /tmp/test-output.json > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Valid JSON file created"
        LEAD_COUNT=$(python3 -c "import json; data = json.load(open('/tmp/test-output.json')); print(len(data))")
        echo -e "  ${GREEN}✓${NC} Contains $LEAD_COUNT leads"
    else
        echo -e "  ${RED}✗${NC} Invalid JSON file"
    fi
    rm -f /tmp/test-output.json
else
    echo -e "  ${RED}✗${NC} JSON file not created"
fi
echo ""

# Test 10: CSV export
echo "Step 10: Running CSV export..."
run_test "leedhunter export (CSV)" "leedhunter export --format csv --output /tmp/test-output.csv --objective 'Find auto importers in Tehran'" 0

# Verify CSV file
if [ -f /tmp/test-output.csv ]; then
    LINE_COUNT=$(wc -l < /tmp/test-output.csv)
    if [ $LINE_COUNT -gt 1 ]; then
        echo -e "  ${GREEN}✓${NC} Valid CSV file created with $((LINE_COUNT - 1)) leads"
    else
        echo -e "  ${YELLOW}⚠${NC} CSV file created but may be empty"
    fi
    rm -f /tmp/test-output.csv
else
    echo -e "  ${RED}✗${NC} CSV file not created"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "LeedHunter is installed correctly and working properly."
    echo ""
    echo "Next steps:"
    echo "  1. Try different search queries"
    echo "  2. Explore the CLI options (leedhunter <command> --help)"
    echo "  3. Read the user guide: docs/user-guide.md"
    echo "  4. (Optional) Configure real search providers for production use"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Please check the error messages above and:"
    echo "  1. Ensure all dependencies are installed: pip install -e \".[dev]\""
    echo "  2. Check Python version (>= 3.10 required)"
    echo "  3. See troubleshooting in docs/first-user-acceptance-test.md"
    exit 1
fi
