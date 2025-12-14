import pandas as pd  # Using pandas for clear tabular output


def map_vas_to_label(V, A, S):
    """
    Maps a continuous VAS vector (V, A, S) to a discrete emotion label
    based on simple IF/ELSE boundaries derived from the VAS model document (VAS.pdf).
    V: Valence (-1 to +1), A: Arousal (0 to 1), S: Sociality (-1 to +1).
    """

    # 1. High Arousal, Strong Emotions (V > 0.7 or V < -0.7)
    if A > 0.6:
        if V > 0.7:
            # High V (+1.0), High A (0.6), High S (+1.0) -> Love/Ecstasy
            if S > 0.5:
                return "Love/Ecstasy"
            # High V (+1.0), High A (0.6), Low S (-1.0) -> Elation/Excitement (non-social)
            else:
                return "Excitement/Elation"
        elif V < -0.7:
            # Low V (-0.7), High A (1.0), High S (+0.7) -> Anger/Rage
            if S > 0.5:
                return "Anger/Rage"
            # Low V (-0.7), High A (1.0), Low S (-0.9) -> Fear/Terror
            elif S < -0.5:
                return "Fear/Terror"
            else:
                return "Distress/Anxiety"

    # 2. Moderate/Low Arousal, Strong Valence (V > 0.7 or V < -0.7)
    # A <= 0.6 (Low/Moderate Arousal)
    if V > 0.7:
        # High V (+1.0), Low A (0.0) -> Serenity/Contentment
        return "Serenity/Contentment"
    elif V < -0.7:
        # Low V (-0.7), Low A (0.3) -> Sadness/Grief
        return "Sadness/Grief"

    # 3. Moderate Valence / Neutral (Valence between -0.7 and 0.7)

    # Check for Disgust/Aversion (V is mid-negative, A is moderate, S is avoid)
    if V < -0.4 and A >= 0.5 and S < -0.7:
        # Disgust: (-0.5, 0.7, -0.9)
        return "Disgust/Aversion"

    # Neutral/Calm/Boredom
    if A < 0.3:
        # Low Arousal -> Calmness or Apathy
        if -0.2 <= V <= 0.2:
            return "Calmness/Apathy"
        elif V > 0.2:
            return "Relaxation"
        else:
            return "Boredom/Dullness"

    # Default/Uncategorized (e.g., moderate activation, moderate valence, neutral sociality)
    return "Interest/Ambivalence"


def main():
    """Defines and runs a series of tests for the VAS emotion mapping."""

    # Test cases including the anchors from the VAS.pdf document.
    test_cases = [
        # Anchor Emotions (from VAS.pdf, page 1)
        {"V": 1.0, "A": 0.6, "S": 1.0, "Name": "Love (Anchor)", "Expected": "Love/Ecstasy"},  # Love: (+1.0, 0.6, +1.0)
        {"V": -0.7, "A": 1.0, "S": 0.7, "Name": "Anger (Anchor)", "Expected": "Anger/Rage"},  # Anger: (-0.7, 1.0, +0.7)
        {"V": -0.5, "A": 0.7, "S": -0.9, "Name": "Disgust (Anchor)", "Expected": "Disgust/Aversion"},
        # Disgust: (-0.5, 0.7, -0.9)

        # Case Study Example (from VAS.pdf, page 3-4)
        {"V": -0.18, "A": 0.42, "S": -0.028, "Name": "Case Study Outcome (Annoyance)",
         "Expected": "Interest/Ambivalence"},  # V=-0.18, A=0.42, S=-0.028

        # Other Key Emotion Quadrants
        {"V": 0.8, "A": 0.1, "S": 0.5, "Name": "Serenity", "Expected": "Serenity/Contentment"},  # High V, Low A
        {"V": 0.0, "A": 0.0, "S": 0.0, "Name": "Neutral Calm", "Expected": "Calmness/Apathy"},  # Neutral V, Low A
        {"V": -0.9, "A": 0.9, "S": -0.9, "Name": "Terror/Fear", "Expected": "Fear/Terror"},  # Low V, High A, Avoid S
        {"V": -0.8, "A": 0.3, "S": -0.2, "Name": "Grief/Sadness", "Expected": "Sadness/Grief"},  # Low V, Low A
    ]

    results = []

    print("--- Running VAS Emotion Mapping Tests ---\n")

    for case in test_cases:
        V, A, S = case["V"], case["A"], case["S"]

        # Run the function
        actual_label = map_vas_to_label(V, A, S)

        # Determine if the test passed
        is_pass = actual_label == case["Expected"]

        # Store results
        results.append({
            "Test Case": case["Name"],
            "V": V,
            "A": A,
            "S": S,
            "Expected Label": case["Expected"],
            "Actual Label": actual_label,
            "Status": "PASS" if is_pass else f"FAIL (Got: {actual_label})"
        })

    # Print results in a table
    df = pd.DataFrame(results)

    # Set display options for full table visibility
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    print(df.to_string(index=False))

    # Summary
    failed_count = len(df[df['Status'].str.startswith('FAIL')])
    total_count = len(df)

    print(f"\n--- Test Summary ---")
    print(f"Total Tests Run: {total_count}")
    print(f"Total Tests Passed: {total_count - failed_count}")
    print(f"Total Tests Failed: {failed_count}")
    print(f"Result: {'SUCCESS' if failed_count == 0 else 'FAILURE'}")


if __name__ == "__main__":
    main()