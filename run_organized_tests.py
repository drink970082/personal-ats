#!/usr/bin/env python3
"""
Test runner for the organized ATS Dashboard test suite.
"""

import subprocess
import sys
import os
import time
from pathlib import Path


def ensure_dependencies():
    """Ensure all test dependencies are installed."""
    print("📦 Installing test dependencies...")
    
    # Install from requirements file
    requirements_file = Path(__file__).parent / "requirements-test.txt"
    if requirements_file.exists():
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                         check=True, capture_output=True)
            print("✅ Test dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    # Install Playwright browsers
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                     check=True, capture_output=True)
        print("✅ Playwright browsers installed")
    except subprocess.CalledProcessError:
        print("⚠️  Warning: Could not install Playwright browsers")
    
    return True


def run_test_suite(test_type=None, verbose=False, coverage=False):
    """Run the test suite with various options."""
    
    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Add test type specific options
    if test_type == "unit":
        cmd.extend(["-m", "unit", "tests/unit/"])
        print("🧪 Running Unit Tests...")
        
    elif test_type == "integration":
        cmd.extend(["-m", "integration", "tests/integration/"])
        print("🔗 Running Integration Tests...")
        
    elif test_type == "database":
        cmd.extend(["-m", "database", "tests/database/"])
        print("💾 Running Database Tests...")
        
    elif test_type == "callbacks":
        cmd.extend(["-m", "callbacks", "tests/callbacks/"])
        print("⚡ Running Callback Tests...")
        
    elif test_type == "e2e":
        cmd.extend(["-m", "e2e", "tests/e2e/"])
        print("🌐 Running E2E Tests...")
        
    elif test_type == "fast":
        cmd.extend(["-m", "not slow and not e2e", "tests/"])
        print("⚡ Running Fast Tests...")
        
    elif test_type == "slow":
        cmd.extend(["-m", "slow", "tests/"])
        print("🐌 Running Slow Tests...")
        
    else:
        cmd.append("tests/")
        print("🎯 Running All Tests...")
    
    # Run the tests
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Tests completed successfully in {duration:.2f}s")
        else:
            print(f"❌ Tests failed after {duration:.2f}s")
            
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_parallel_tests():
    """Run tests in parallel for faster execution."""
    print("🚀 Running tests in parallel...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-n", "auto",  # Use all available CPUs
        "-v",
        "tests/"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running parallel tests: {e}")
        return False


def generate_test_report():
    """Generate comprehensive test report."""
    print("📊 Generating test report...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "--html=test_report.html",
        "--self-contained-html",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--tb=short",
        "tests/"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print("✅ Test report generated: test_report.html")
            print("✅ Coverage report generated: htmlcov/index.html")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False


def main():
    """Main test runner entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ATS Dashboard Test Runner")
    parser.add_argument("--type", choices=[
        "unit", "integration", "database", "callbacks", "e2e", "fast", "slow"
    ], help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--report", "-r", action="store_true", help="Generate comprehensive report")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies only")
    
    args = parser.parse_args()
    
    print("🧪 ATS Dashboard Test Suite Runner")
    print("=" * 50)
    
    # Install dependencies if requested
    if args.install_deps:
        ensure_dependencies()
        return
    
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    
    # Check if dependencies need to be installed
    try:
        import pytest
        import playwright
    except ImportError:
        print("📦 Missing dependencies, installing...")
        if not ensure_dependencies():
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    success = True
    
    if args.report:
        success = generate_test_report()
    elif args.parallel:
        success = run_parallel_tests()
    else:
        success = run_test_suite(
            test_type=args.type,
            verbose=args.verbose,
            coverage=args.coverage
        )
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 