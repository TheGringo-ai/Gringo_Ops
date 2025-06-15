from tools.gemini_agent import query_model, write_to_memory

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--go", action="store_true", help="Trigger a Gemini prompt")
    parser.add_argument("--apply", action="store_true", help="Write to memory after query")
    args = parser.parse_args()

    if args.go:
        prompt = input("Enter your Gemini task:\n> ")
        result = query_model(prompt, record_to_memory=args.apply)
        print("\n💡 Gemini Response:\n", result)
