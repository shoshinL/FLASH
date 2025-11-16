"""
Comprehensive integration tests for multi-provider LLM support.

Usage:
1. Copy test_config_template.py to test_config_local.py
2. Add your API keys to test_config_local.py
3. Run: python test_providers.py

This will generate a detailed test report in test_results.json and test_report.md
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from test_config_local import API_KEYS, TEST_MODELS, THINKING_MODELS, TEST_SETTINGS, TEST_QUESTIONS, TEST_DOCUMENT_CHUNK, TEST_EMBEDDING_MODELS
except ImportError:
    print("❌ ERROR: test_config_local.py not found!")
    print("📝 Please copy test_config_template.py to test_config_local.py and add your API keys.")
    sys.exit(1)

from settingUtils.llm_provider import ProviderFactory
from agents.parser_utils import preprocess_llm_output, strip_thinking_traces, create_thinking_aware_parser
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


class TestResults:
    """Class to track and format test results."""

    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        self.provider_stats = {}

    def add_result(self, test_name: str, provider: str, status: str,
                   duration: float, details: Dict[str, Any]):
        """Add a test result."""
        self.results.append({
            "test_name": test_name,
            "provider": provider,
            "status": status,  # "PASS", "FAIL", "SKIP"
            "duration": duration,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

        # Update stats
        if provider not in self.provider_stats:
            self.provider_stats[provider] = {"pass": 0, "fail": 0, "skip": 0, "total": 0}
        self.provider_stats[provider][status.lower()] += 1
        self.provider_stats[provider]["total"] += 1

    def generate_report(self) -> str:
        """Generate a markdown report."""
        duration = (datetime.now() - self.start_time).total_seconds()

        report = f"""# Multi-Provider LLM Integration Test Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Duration**: {duration:.2f} seconds
**Total Tests**: {len(self.results)}

## Summary by Provider

"""

        for provider, stats in sorted(self.provider_stats.items()):
            pass_rate = (stats['pass'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status_icon = "✅" if pass_rate == 100 else "⚠️" if pass_rate >= 70 else "❌"

            report += f"""### {status_icon} {provider.upper()}
- **Total Tests**: {stats['total']}
- **Passed**: {stats['pass']} ✅
- **Failed**: {stats['fail']} ❌
- **Skipped**: {stats['skip']} ⏭️
- **Pass Rate**: {pass_rate:.1f}%

"""

        report += "\n## Detailed Test Results\n\n"

        for result in self.results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}[result["status"]]
            report += f"""### {status_icon} {result['test_name']} - {result['provider']}
**Status**: {result['status']}
**Duration**: {result['duration']:.2f}s

"""

            if result['details']:
                report += "**Details**:\n```\n"
                for key, value in result['details'].items():
                    report += f"{key}: {value}\n"
                report += "```\n\n"

        # Add recommendations
        report += "\n## Recommendations\n\n"

        for provider, stats in sorted(self.provider_stats.items()):
            if stats['fail'] > 0:
                report += f"- ⚠️ **{provider}**: {stats['fail']} test(s) failed. Check API key and model availability.\n"
            elif stats['skip'] > 0:
                report += f"- ℹ️ **{provider}**: {stats['skip']} test(s) skipped. Add API key to test_config_local.py.\n"
            else:
                report += f"- ✅ **{provider}**: All tests passed!\n"

        return report

    def save_results(self, json_path: str = "test_results.json", md_path: str = "test_report.md"):
        """Save results to files."""
        # Save JSON
        with open(json_path, 'w') as f:
            json.dump({
                "summary": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "total_tests": len(self.results),
                    "provider_stats": self.provider_stats
                },
                "results": self.results
            }, f, indent=2)

        # Save Markdown
        with open(md_path, 'w') as f:
            f.write(self.generate_report())

        print(f"\n📊 Results saved to {json_path} and {md_path}")


# Test data models
class Questions(BaseModel):
    Questions: List[str] = Field(description="List of questions")


def test_provider_initialization(provider_name: str, api_key: Optional[str], results: TestResults):
    """Test 1: Provider initialization."""
    test_name = "Provider Initialization"
    start_time = time.time()

    try:
        if provider_name != "ollama" and not api_key:
            results.add_result(test_name, provider_name, "SKIP", 0,
                             {"reason": "No API key provided"})
            return None

        provider = ProviderFactory.get_provider(
            provider_name,
            api_key=api_key,
            model=TEST_MODELS.get(provider_name)
        )

        duration = time.time() - start_time
        results.add_result(test_name, provider_name, "PASS", duration,
                         {"model": TEST_MODELS.get(provider_name)})
        return provider

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(test_name, provider_name, "FAIL", duration,
                         {"error": str(e), "traceback": traceback.format_exc()})
        return None


def test_api_key_validation(provider_name: str, api_key: Optional[str], results: TestResults):
    """Test 2: API key validation."""
    test_name = "API Key Validation"
    start_time = time.time()

    try:
        if provider_name != "ollama" and not api_key:
            results.add_result(test_name, provider_name, "SKIP", 0,
                             {"reason": "No API key provided"})
            return

        provider = ProviderFactory.get_provider(
            provider_name,
            api_key=api_key,
            model=TEST_MODELS.get(provider_name)
        )

        is_valid = provider.validate_api_key()
        duration = time.time() - start_time

        if is_valid:
            results.add_result(test_name, provider_name, "PASS", duration,
                             {"validated": True})
        else:
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"validated": False, "reason": "Validation returned False"})

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(test_name, provider_name, "FAIL", duration,
                         {"error": str(e), "traceback": traceback.format_exc()})


def test_model_listing(provider_name: str, api_key: Optional[str], results: TestResults):
    """Test 3: Model listing."""
    test_name = "Model Listing"
    start_time = time.time()

    try:
        if provider_name != "ollama" and not api_key:
            results.add_result(test_name, provider_name, "SKIP", 0,
                             {"reason": "No API key provided"})
            return

        provider = ProviderFactory.get_provider(
            provider_name,
            api_key=api_key,
            model=TEST_MODELS.get(provider_name)
        )

        models = provider.get_available_models()
        duration = time.time() - start_time

        if models and len(models) > 0:
            results.add_result(test_name, provider_name, "PASS", duration,
                             {"model_count": len(models), "sample_models": models[:5]})
        else:
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"reason": "No models returned", "models": models})

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(test_name, provider_name, "FAIL", duration,
                         {"error": str(e), "traceback": traceback.format_exc()})


def test_basic_llm_call(provider_name: str, api_key: Optional[str], results: TestResults):
    """Test 4: Basic LLM call."""
    test_name = "Basic LLM Call"
    start_time = time.time()

    try:
        if provider_name != "ollama" and not api_key:
            results.add_result(test_name, provider_name, "SKIP", 0,
                             {"reason": "No API key provided"})
            return

        provider = ProviderFactory.get_provider(
            provider_name,
            api_key=api_key,
            model=TEST_MODELS.get(provider_name)
        )

        llm = provider.get_llm()
        response = llm.invoke("What is 2+2? Answer with just the number.")

        duration = time.time() - start_time

        if response and response.content:
            results.add_result(test_name, provider_name, "PASS", duration,
                             {"response_length": len(response.content),
                              "response_preview": response.content[:100]})
        else:
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"reason": "Empty response", "response": str(response)})

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(test_name, provider_name, "FAIL", duration,
                         {"error": str(e), "traceback": traceback.format_exc()})


def test_json_parsing(provider_name: str, api_key: Optional[str], results: TestResults):
    """Test 5: JSON output parsing."""
    test_name = "JSON Parsing"
    start_time = time.time()

    try:
        if provider_name != "ollama" and not api_key:
            results.add_result(test_name, provider_name, "SKIP", 0,
                             {"reason": "No API key provided"})
            return

        provider = ProviderFactory.get_provider(
            provider_name,
            api_key=api_key,
            model=TEST_MODELS.get(provider_name)
        )

        llm = provider.get_llm()
        parser = JsonOutputParser(pydantic_object=Questions)

        prompt = f"""Generate 3 simple questions about basic math.

        {parser.get_format_instructions()}

        Return ONLY the JSON, no other text."""

        response = llm.invoke(prompt)
        parsed = parser.parse(response.content)

        duration = time.time() - start_time

        if parsed and 'Questions' in parsed and len(parsed['Questions']) > 0:
            results.add_result(test_name, provider_name, "PASS", duration,
                             {"questions_generated": len(parsed['Questions']),
                              "sample": parsed['Questions'][0] if parsed['Questions'] else None})
        else:
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"reason": "Invalid parsed output", "parsed": str(parsed)})

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(test_name, provider_name, "FAIL", duration,
                         {"error": str(e), "traceback": traceback.format_exc()})


def test_thinking_trace_removal(provider_name: str, api_key: Optional[str], results: TestResults):
    """Test 6: Thinking trace removal."""
    test_name = "Thinking Trace Removal"
    start_time = time.time()

    try:
        # Test with sample thinking traces
        test_cases = [
            ("<think>Let me think...</think>\n{\"Questions\": [\"Q1\"]}",
             "{\"Questions\": [\"Q1\"]}"),
            ("{\"thinking\": \"hmm...\", \"Questions\": [\"Q1\"]}",
             "{\"Questions\": [\"Q1\"]}"),
            ("<thinking>Process...</thinking>\nAnswer: 42",
             "Answer: 42"),
        ]

        all_passed = True
        failed_cases = []

        for input_text, expected_contains in test_cases:
            cleaned = strip_thinking_traces(input_text)
            if expected_contains not in cleaned:
                all_passed = False
                failed_cases.append({
                    "input": input_text[:50],
                    "expected_contains": expected_contains,
                    "got": cleaned[:50]
                })

        duration = time.time() - start_time

        if all_passed:
            results.add_result(test_name, provider_name, "PASS", duration,
                             {"test_cases": len(test_cases), "all_passed": True})
        else:
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"failed_cases": failed_cases})

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(test_name, provider_name, "FAIL", duration,
                         {"error": str(e), "traceback": traceback.format_exc()})


def test_embedding_support(provider_name: str, api_key: Optional[str], results: TestResults):
    """Test 7: Embedding model support."""
    test_name = "Embedding Support"
    start_time = time.time()

    try:
        if provider_name != "ollama" and not api_key:
            duration = time.time() - start_time
            results.add_result(test_name, provider_name, "SKIP", duration,
                             {"reason": "No API key provided"})
            print(f"  ⏭️  {test_name}: SKIP (no API key)")
            return

        # Get provider instance
        if provider_name == "ollama":
            provider = ProviderFactory.get_provider(provider_name)
        else:
            provider = ProviderFactory.get_provider(provider_name, api_key=api_key)

        # Check if provider supports embeddings
        supports_embeddings = provider.supports_embeddings()

        duration = time.time() - start_time

        # All providers should now support embeddings
        if supports_embeddings:
            results.add_result(test_name, provider_name, "PASS", duration,
                             {"supports_embeddings": True})
            print(f"  ✅ {test_name}: PASS")
        else:
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"reason": "Provider should support embeddings but doesn't",
                              "supports_embeddings": False})
            print(f"  ❌ {test_name}: FAIL")

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(test_name, provider_name, "FAIL", duration,
                         {"error": str(e), "traceback": traceback.format_exc()})
        print(f"  ❌ {test_name}: FAIL - {str(e)}")


def test_embedding_generation(provider_name: str, api_key: Optional[str], results: TestResults):
    """Test 8: Embedding generation (for providers that support it)."""
    test_name = "Embedding Generation"
    start_time = time.time()

    try:
        # Skip if provider not in TEST_EMBEDDING_MODELS
        if provider_name not in TEST_EMBEDDING_MODELS:
            duration = time.time() - start_time
            results.add_result(test_name, provider_name, "SKIP", duration,
                             {"reason": f"No embedding model configured for {provider_name} in TEST_EMBEDDING_MODELS"})
            print(f"  ⏭️  {test_name}: SKIP (no embedding model configured)")
            return

        if provider_name != "ollama" and not api_key:
            duration = time.time() - start_time
            results.add_result(test_name, provider_name, "SKIP", duration,
                             {"reason": "No API key provided"})
            print(f"  ⏭️  {test_name}: SKIP (no API key)")
            return

        # Get configured embedding model
        embedding_model = TEST_EMBEDDING_MODELS[provider_name]

        # Get provider instance
        if provider_name == "ollama":
            provider = ProviderFactory.get_provider(provider_name)
        else:
            provider = ProviderFactory.get_provider(provider_name, api_key=api_key)

        # Verify provider supports embeddings
        if not provider.supports_embeddings():
            duration = time.time() - start_time
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"reason": f"{provider_name} does not support embeddings"})
            print(f"  ❌ {test_name}: FAIL (no embedding support)")
            return

        # Get available embedding models to verify configured model exists
        available_models = provider.get_available_embedding_models()

        if not available_models:
            duration = time.time() - start_time
            if provider_name == "ollama":
                results.add_result(test_name, provider_name, "SKIP", duration,
                                 {"reason": "No Ollama embedding models installed",
                                  "suggestion": f"Run: ollama pull {embedding_model}"})
                print(f"  ⏭️  {test_name}: SKIP (no Ollama embedding models)")
            else:
                results.add_result(test_name, provider_name, "FAIL", duration,
                                 {"reason": "No embedding models available"})
                print(f"  ❌ {test_name}: FAIL (no models)")
            return

        # Warn if configured model not in available models (but still try to use it)
        if embedding_model not in available_models:
            print(f"  ⚠️  Warning: Configured model '{embedding_model}' not found in available models: {available_models}")
            print(f"      Will attempt to use it anyway...")

        # Create embeddings instance
        embeddings = provider.get_embeddings(model=embedding_model)

        # Test embedding generation with sample text
        test_text = "This is a test sentence for embedding generation."
        embedding_vector = embeddings.embed_query(test_text)

        duration = time.time() - start_time

        # Verify embedding is a list/array of numbers
        if isinstance(embedding_vector, (list, tuple)) and len(embedding_vector) > 0:
            results.add_result(test_name, provider_name, "PASS", duration,
                             {"model": embedding_model,
                              "embedding_dimension": len(embedding_vector),
                              "sample_values": str(embedding_vector[:3])})
            print(f"  ✅ {test_name}: PASS (model: {embedding_model}, dim: {len(embedding_vector)})")
        else:
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"reason": "Invalid embedding format",
                              "embedding_type": type(embedding_vector).__name__})
            print(f"  ❌ {test_name}: FAIL (invalid embedding)")

    except Exception as e:
        duration = time.time() - start_time
        if "ollama" in str(e).lower() and provider_name == "ollama":
            results.add_result(test_name, provider_name, "SKIP", duration,
                             {"reason": "Ollama not running or model not available",
                              "error": str(e)})
            print(f"  ⏭️  {test_name}: SKIP (Ollama not available)")
        else:
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"error": str(e), "traceback": traceback.format_exc()})
            print(f"  ❌ {test_name}: FAIL - {str(e)}")


def test_thinking_model(provider_name: str, api_key: Optional[str], results: TestResults):
    """Test 9: Thinking model support (if enabled)."""
    test_name = "Thinking Model Support"

    if not TEST_SETTINGS.get("test_thinking_models", False):
        results.add_result(test_name, provider_name, "SKIP", 0,
                         {"reason": "Thinking model tests disabled in config"})
        return

    if provider_name not in THINKING_MODELS:
        results.add_result(test_name, provider_name, "SKIP", 0,
                         {"reason": f"No thinking model configured for {provider_name}"})
        return

    start_time = time.time()

    try:
        if not api_key:
            results.add_result(test_name, provider_name, "SKIP", 0,
                             {"reason": "No API key provided"})
            return

        provider = ProviderFactory.get_provider(
            provider_name,
            api_key=api_key,
            model=THINKING_MODELS[provider_name]
        )

        llm = provider.get_llm()
        parser = JsonOutputParser(pydantic_object=Questions)
        thinking_parser = create_thinking_aware_parser(parser, llm)

        prompt = f"""Analyze this problem carefully and generate 2 questions about it:
        "What is the sum of all even numbers between 1 and 10?"

        {parser.get_format_instructions()}"""

        response = llm.invoke(prompt)
        parsed = thinking_parser.parse(response.content)

        duration = time.time() - start_time

        if parsed and 'Questions' in parsed:
            results.add_result(test_name, provider_name, "PASS", duration,
                             {"model": THINKING_MODELS[provider_name],
                              "questions_generated": len(parsed['Questions'])})
        else:
            results.add_result(test_name, provider_name, "FAIL", duration,
                             {"reason": "Failed to parse thinking model output",
                              "response_preview": str(response.content)[:200]})

    except Exception as e:
        duration = time.time() - start_time
        results.add_result(test_name, provider_name, "FAIL", duration,
                         {"error": str(e), "traceback": traceback.format_exc()})


def run_all_tests():
    """Run all tests for all providers."""
    print("=" * 70)
    print("🧪 FLASH Multi-Provider Integration Test Suite")
    print("=" * 70)
    print()

    results = TestResults()

    providers = ["openai", "anthropic", "google", "openrouter", "ollama"]

    for provider in providers:
        print(f"\n{'='*70}")
        print(f"Testing Provider: {provider.upper()}")
        print(f"{'='*70}\n")

        api_key = API_KEYS.get(provider)

        # Run all tests for this provider
        test_provider_initialization(provider, api_key, results)
        test_api_key_validation(provider, api_key, results)
        test_model_listing(provider, api_key, results)
        test_basic_llm_call(provider, api_key, results)
        test_json_parsing(provider, api_key, results)
        test_thinking_trace_removal(provider, api_key, results)
        test_embedding_support(provider, api_key, results)
        test_embedding_generation(provider, api_key, results)
        test_thinking_model(provider, api_key, results)

        # Print provider summary
        stats = results.provider_stats.get(provider, {})
        print(f"\n{provider.upper()} Summary: {stats.get('pass', 0)} passed, "
              f"{stats.get('fail', 0)} failed, {stats.get('skip', 0)} skipped")

    print(f"\n{'='*70}")
    print("📊 Generating Reports...")
    print(f"{'='*70}\n")

    results.save_results()

    # Print summary
    print("\n" + "="*70)
    print("✅ TEST SUITE COMPLETE")
    print("="*70)
    print(f"\nTotal Tests Run: {len(results.results)}")

    total_pass = sum(s['pass'] for s in results.provider_stats.values())
    total_fail = sum(s['fail'] for s in results.provider_stats.values())
    total_skip = sum(s['skip'] for s in results.provider_stats.values())

    print(f"Passed: {total_pass} ✅")
    print(f"Failed: {total_fail} ❌")
    print(f"Skipped: {total_skip} ⏭️")

    if total_fail == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total_fail} test(s) failed. Check test_report.md for details.")

    print("\n📝 Next steps:")
    print("1. Review test_report.md for detailed results")
    print("2. Check test_results.json for machine-readable output")
    print("3. Fix any failed tests and re-run")
    print()


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
