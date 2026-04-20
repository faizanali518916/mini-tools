import json
import os


def compare_json_keys():
    # 1. List JSON files in the current directory
    files = [f for f in os.listdir(".") if f.endswith(".json")]

    if not files:
        print("No JSON files found in the directory.")
        return

    print("--- Available JSON Files ---")
    for i, file in enumerate(files):
        print(f"{i}: {file}")

    # 2. Selection: Files
    try:
        choices = input("\nEnter file numbers to compare (e.g., 0, 2): ")
        selected_indices = [int(x.strip()) for x in choices.split(",")]
        selected_files = [files[i] for i in selected_indices]
    except (ValueError, IndexError):
        print("Invalid file selection.")
        return

    # 3. Selection: Level of Analysis (Scope)
    print("\n--- Select Level of Analysis ---")
    print("1: data (Root object)")
    print("2: product_details")
    print("3: product_information")
    print("4: rating_distribution")

    scope_choice = input("\nSelect scope (1-4): ").strip()

    # Map choices to the JSON keys
    scope_map = {
        "1": "data",
        "2": "product_details",
        "3": "product_information",
        "4": "rating_distribution",
    }

    target_key = scope_map.get(scope_choice)
    if not target_key:
        print("Invalid scope selection.")
        return

    print(f"\nAnalyzing keys within: '{target_key}'")

    # 4. Read data and extract keys based on scope
    file_key_map = {}

    for file_name in selected_files:
        try:
            with open(file_name, "r") as f:
                content = json.load(f)

                # Logic: If they chose 'data', we look at content['data']
                # If they chose anything else, we look at content['data'][choice]
                if target_key == "data":
                    data_obj = content.get("data", {})
                else:
                    # Navigate into data -> specific_key
                    root_data = content.get("data", {})
                    data_obj = root_data.get(target_key, {})

                if isinstance(data_obj, dict):
                    file_key_map[file_name] = set(data_obj.keys())
                else:
                    print(
                        f"Warning: '{target_key}' in {file_name} is not a dictionary. Skipping."
                    )
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

    if not file_key_map:
        print("No valid data found in the selected scope.")
        return

    # 5. Compare Keys using Set Logic
    all_sets = list(file_key_map.values())
    common_keys = set.intersection(*all_sets) if all_sets else set()

    print("\n" + "=" * 40)
    print(f"RESULTS FOR SCOPE: {target_key}")
    print("=" * 40)

    print(f"\nCOMMON KEYS ({len(common_keys)}):")
    if common_keys:
        for k in sorted(list(common_keys)):
            print(f" - {k}")
    else:
        print(" None")

    print("\nUNIQUE KEYS (Not present in all files):")
    for file_name, keys in file_key_map.items():
        unique_to_this_file = keys - common_keys
        print(f"\n--- {file_name} ---")
        if unique_to_this_file:
            for k in sorted(list(unique_to_this_file)):
                print(f" + {k}")
        else:
            print(" No unique keys")


if __name__ == "__main__":
    compare_json_keys()
