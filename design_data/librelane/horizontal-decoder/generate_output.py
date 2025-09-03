def generate_output_file(N, value, filename="output.txt"):
    with open(filename, "w") as f:
        for i in range(N + 1):
            f.write(f"output_o\\[{i}\\]\n")
            f.write(f"output_no\\[{i}\\]\n")
            f.write(f"${value}\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate output file with repeated pattern using escaped brackets.")
    parser.add_argument("--N", type=int, required=True, help="Maximum index (inclusive).")
    parser.add_argument("--value", type=str, required=True, help="Value to substitute for 9.")
    parser.add_argument("--filename", type=str, default="output.txt", help="Output filename.")

    args = parser.parse_args()
    generate_output_file(args.N, args.value, args.filename)
