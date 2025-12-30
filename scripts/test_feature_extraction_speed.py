import logging
import time

from infrastructure.ml.feature_engineering import extract_property_features

# Configure logging to see our HIT logs
logging.basicConfig(level=logging.INFO)


def test_speed():
    # 1. Optimized Input
    optimized_input = "RICHIESTA VALUTAZIONE: Via Dante 12 (Condizione: excellent) MQ: 120"
    print(f"\n--- Testing Optimized Input ---\n'{optimized_input}'")

    start_time = time.time()
    features = extract_property_features(optimized_input, address="Via Dante 12")
    end_time = time.time()

    print(f"Time detected: {end_time - start_time:.4f} seconds")
    print(f"Extracted: {features}")

    if (end_time - start_time) < 0.1:
        print("✅ SPEED CHECK PASSED (<0.1s)")
    else:
        print("❌ SPEED CHECK FAILED (>0.1s)")

    # 2. Unstructured Input (LLM Fallback) - skipping to save tokens if first passed,
    # but good to verify it doesnt break.
    unstructured_input = "Vorrei sapere quanto vale il mio trilocale in centro a Milano"
    print(f"\n--- Testing Unstructured Input (LLM Fallback) ---\n'{unstructured_input}'")

    start_time = time.time()
    try:
        features_llm = extract_property_features(unstructured_input)
        end_time = time.time()
        print(f"Time detected: {end_time - start_time:.4f} seconds")
        print(f"Extracted: {features_llm}")
    except Exception as e:
        print(f"LLM Call failed (expected if no API key or network): {e}")


if __name__ == "__main__":
    test_speed()
