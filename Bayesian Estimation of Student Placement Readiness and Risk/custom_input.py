from bayesian_network import BayesianNetwork

def get_user_choice(prompt, options):
    """Utility to display choices and get valid user input."""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")

    while True:
        try:
            choice = int(input("\nEnter choice number: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    print("\n" + "="*70)
    print(" CUSTOM INPUT: STUDENT PLACEMENT READINESS PREDICTOR")
    print("="*70)

    bn = BayesianNetwork("cpt_data.json")

    mock_options = ["Excellent", "Good", "Average", "Poor"]
    consistency_options = ["HighlyConsistent", "Moderate", "Irregular", "Rare"]
    rejections_options = ["None", "1-2", "3-5", "MoreThan5"]
    resume_options = ["High", "Medium", "Low"]

    evidence = {}

    evidence["MockPerformance"] = get_user_choice(
        "Select Mock Performance:", mock_options
    )

    evidence["Consistency"] = get_user_choice(
        "Select Preparation Consistency:", consistency_options
    )

    evidence["Rejections"] = get_user_choice(
        "Select Recent Rejections Count:", rejections_options
    )

    evidence["ResumeQuality"] = get_user_choice(
        "Select Resume Quality (ATS Score Range):", resume_options
    )

    print("\nRunning Bayesian Inference...\n")
    result = bn.inference(evidence)

    report = bn.generate_report(evidence, result)

    print(report)

    save = input("\nDo you want to save this report? (y/n): ").strip().lower()
    if save == "y":
        with open("custom_input_report.txt", "w") as f:
            f.write(report)
        print("✓ Report saved as 'custom_input_report.txt'")

if __name__ == "__main__":
    main()
