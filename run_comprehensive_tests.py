#!/usr/bin/env python3
"""
Comprehensive Test Runner for ATS Dashboard
Runs all test suites including unit, integration, backend, and E2E tests with detailed reporting.
"""

import subprocess
import sys
import os
import time
from pathlib import Path


def install_dependencies():
    """Install test dependencies."""
    print("📦 Installing test dependencies...")
    
    dependencies = [
        'pytest>=7.0.0',
        'selenium>=4.0.0',
        'webdriver-manager>=3.8.0',
        'requests>=2.25.0',
        'psutil>=5.8.0',  # For memory testing in backend tests
    ]
    
    for dep in dependencies:
        try:
            print(f"  Installing {dep}...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Warning: Failed to install {dep}: {e}")
    
    print("✅ Dependencies installation completed")


def run_test_suite(test_file, suite_name, description):
    """Run a specific test suite and return results."""
    print(f"\n🧪 Running {suite_name}")
    print(f"   {description}")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            test_file,
            '-v',
            '--tb=short',
            '--durations=10',  # Show 10 slowest tests
            '--strict-markers',
            '--disable-warnings'
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Parse results
        output_lines = result.stdout.split('\n')
        
        # Count test results
        passed = len([line for line in output_lines if ' PASSED' in line])
        failed = len([line for line in output_lines if ' FAILED' in line])
        skipped = len([line for line in output_lines if ' SKIPPED' in line])
        errors = len([line for line in output_lines if ' ERROR' in line])
        
        total = passed + failed + skipped + errors
        
        # Determine status
        if result.returncode == 0:
            status = "✅ PASSED"
            status_color = "\033[92m"  # Green
        else:
            status = "❌ FAILED"
            status_color = "\033[91m"  # Red
        
        # Print summary
        print(f"\n{status_color}{status}\033[0m")
        print(f"📊 Results: {passed} passed, {failed} failed, {skipped} skipped, {errors} errors")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        # Print failures if any
        if failed > 0 or errors > 0:
            print(f"\n💥 Failures/Errors in {suite_name}:")
            failure_lines = [line for line in output_lines if 'FAILED' in line or 'ERROR' in line]
            for line in failure_lines[:10]:  # Show first 10 failures
                print(f"   {line}")
            
            if len(failure_lines) > 10:
                print(f"   ... and {len(failure_lines) - 10} more")
        
        return {
            'name': suite_name,
            'file': test_file,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'errors': errors,
            'total': total,
            'duration': duration,
            'success': result.returncode == 0,
            'output': result.stdout,
            'error_output': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT - {suite_name} took longer than 5 minutes")
        return {
            'name': suite_name,
            'file': test_file,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 1,
            'total': 1,
            'duration': 300,
            'success': False,
            'output': '',
            'error_output': 'Test suite timed out'
        }
    
    except Exception as e:
        print(f"💥 ERROR running {suite_name}: {e}")
        return {
            'name': suite_name,
            'file': test_file,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 1,
            'total': 1,
            'duration': 0,
            'success': False,
            'output': '',
            'error_output': str(e)
        }


def run_all_tests():
    """Run all comprehensive test suites."""
    print("🚀 ATS Dashboard Comprehensive Test Suite")
    print("=" * 80)
    
    # Install dependencies first
    install_dependencies()
    
    # Define all test suites
    test_suites = [
        {
            'file': 'test_unit.py',
            'name': 'Unit Tests',
            'description': 'Core functionality, filtering, pagination, and business logic'
        },
        {
            'file': 'test_comprehensive.py',
            'name': 'Comprehensive Unit Tests',
            'description': 'Extended unit tests with data validation, performance, and edge cases'
        },
        {
            'file': 'test_backend_comprehensive.py',
            'name': 'Backend & Database Tests',
            'description': 'Database operations, data integrity, validation, and performance'
        },
        {
            'file': 'test_integration_comprehensive.py',
            'name': 'Integration Tests',
            'description': 'Component integration, data consistency, and workflow testing'
        },
        {
            'file': 'test_e2e.py',
            'name': 'End-to-End Tests',
            'description': 'Full UI workflow testing with Selenium WebDriver'
        },
        {
            'file': 'test_e2e_comprehensive.py',
            'name': 'Comprehensive E2E Tests',
            'description': 'Extended E2E tests with advanced scenarios and performance'
        }
    ]
    
    results = []
    
    # Run each test suite
    for suite in test_suites:
        if os.path.exists(suite['file']):
            result = run_test_suite(suite['file'], suite['name'], suite['description'])
            results.append(result)
        else:
            print(f"\n⚠️  Skipping {suite['name']}: {suite['file']} not found")
            results.append({
                'name': suite['name'],
                'file': suite['file'],
                'passed': 0,
                'failed': 0,
                'skipped': 1,
                'errors': 0,
                'total': 1,
                'duration': 0,
                'success': False,
                'output': '',
                'error_output': 'File not found'
            })
    
    # Generate comprehensive report
    generate_comprehensive_report(results)
    
    return results


def generate_comprehensive_report(results):
    """Generate a comprehensive test report."""
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    
    # Calculate totals
    total_passed = sum(r['passed'] for r in results)
    total_failed = sum(r['failed'] for r in results)
    total_skipped = sum(r['skipped'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    total_tests = sum(r['total'] for r in results)
    total_duration = sum(r['duration'] for r in results)
    
    successful_suites = len([r for r in results if r['success']])
    total_suites = len(results)
    
    # Overall status
    overall_success = total_failed == 0 and total_errors == 0
    overall_status = "✅ SUCCESS" if overall_success else "❌ FAILURE"
    status_color = "\033[92m" if overall_success else "\033[91m"
    
    print(f"\n{status_color}{overall_status}\033[0m")
    print(f"📊 Overall Results:")
    print(f"   • Test Suites: {successful_suites}/{total_suites} passed")
    print(f"   • Total Tests: {total_tests}")
    print(f"   • Passed: {total_passed}")
    print(f"   • Failed: {total_failed}")
    print(f"   • Skipped: {total_skipped}")
    print(f"   • Errors: {total_errors}")
    print(f"   • Success Rate: {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
    print(f"   • Total Duration: {total_duration:.2f} seconds")
    
    # Suite breakdown
    print(f"\n📈 Suite Breakdown:")
    for result in results:
        suite_status = "✅" if result['success'] else "❌"
        success_rate = (result['passed']/result['total']*100) if result['total'] > 0 else 0
        print(f"   {suite_status} {result['name']}: {result['passed']}/{result['total']} ({success_rate:.1f}%) - {result['duration']:.2f}s")
    
    # Performance insights
    print(f"\n⚡ Performance Insights:")
    if results:
        slowest_suite = max(results, key=lambda x: x['duration'])
        fastest_suite = min(results, key=lambda x: x['duration'])
        print(f"   • Slowest Suite: {slowest_suite['name']} ({slowest_suite['duration']:.2f}s)")
        print(f"   • Fastest Suite: {fastest_suite['name']} ({fastest_suite['duration']:.2f}s)")
    
    # Coverage analysis
    print(f"\n🎯 Coverage Analysis:")
    coverage_areas = {
        'Unit Testing': any('unit' in r['name'].lower() for r in results),
        'Integration Testing': any('integration' in r['name'].lower() for r in results),
        'Backend Testing': any('backend' in r['name'].lower() for r in results),
        'E2E Testing': any('e2e' in r['name'].lower() for r in results),
        'Performance Testing': any('comprehensive' in r['name'].lower() for r in results),
    }
    
    for area, covered in coverage_areas.items():
        status = "✅" if covered else "❌"
        print(f"   {status} {area}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if total_failed > 0:
        print("   • Fix failing tests before deployment")
    if total_errors > 0:
        print("   • Investigate test errors and infrastructure issues")
    if total_duration > 300:  # 5 minutes
        print("   • Consider optimizing slow tests for faster feedback")
    
    success_rate = (total_passed/total_tests*100) if total_tests > 0 else 0
    if success_rate >= 95:
        print("   • Excellent test coverage! Ready for production 🚀")
    elif success_rate >= 85:
        print("   • Good test coverage. Consider addressing remaining issues")
    else:
        print("   • Test coverage needs improvement before production")
    
    # Save detailed report
    save_detailed_report(results)


def save_detailed_report(results):
    """Save detailed test report to file."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_comprehensive_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        f.write("# ATS Dashboard Comprehensive Test Report\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary
        total_passed = sum(r['passed'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        total_skipped = sum(r['skipped'] for r in results)
        total_errors = sum(r['errors'] for r in results)
        total_tests = sum(r['total'] for r in results)
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Tests**: {total_tests}\n")
        f.write(f"- **Passed**: {total_passed}\n")
        f.write(f"- **Failed**: {total_failed}\n")
        f.write(f"- **Skipped**: {total_skipped}\n")
        f.write(f"- **Errors**: {total_errors}\n")
        f.write(f"- **Success Rate**: {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%\n\n")
        
        # Detailed results
        f.write("## Detailed Results\n\n")
        for result in results:
            f.write(f"### {result['name']}\n\n")
            f.write(f"- **File**: `{result['file']}`\n")
            f.write(f"- **Status**: {'✅ PASSED' if result['success'] else '❌ FAILED'}\n")
            f.write(f"- **Tests**: {result['total']}\n")
            f.write(f"- **Passed**: {result['passed']}\n")
            f.write(f"- **Failed**: {result['failed']}\n")
            f.write(f"- **Duration**: {result['duration']:.2f}s\n\n")
            
            if result['error_output']:
                f.write("**Error Output:**\n")
                f.write(f"```\n{result['error_output']}\n```\n\n")
    
    print(f"\n📄 Detailed report saved to: {report_file}")


if __name__ == "__main__":
    print("Starting comprehensive test execution...")
    results = run_all_tests()
    
    # Exit with appropriate code
    total_failed = sum(r['failed'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    
    if total_failed > 0 or total_errors > 0:
        print(f"\n❌ Test execution completed with failures")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed successfully!")
        sys.exit(0) 