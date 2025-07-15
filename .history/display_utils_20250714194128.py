import os

def print_intro():
    print("=== Resume Keyword Matcher ===\n")
    print("Compare up to 3 resumes against a job description.")
    print("See which resume covers the most important keywords for the job.\n")
    print("Resumes with more keyword matches may stand out more to employers.\n")

def print_single_resume_results(result, job_word_counts):
    print(f"\n=== RESULTS for {os.path.basename(result['resume_path'])} ===")
    print(f"Match Percent: {result['match_percent']:.1f}%\n")
    print(f"Matched Keywords ({result['num_matched']}):")
    print(f"{'Keyword':<20} {'Frequency in JD':>16}")
    print("-" * 36)
    for word in sorted(result['matched'], key=lambda w: (-job_word_counts[w], w)):
        print(f"{word:<20} {job_word_counts[word]:>16}")
    print(f"\nMissing Keywords ({result['num_missing']}):")
    print(f"{'Keyword':<20} {'Frequency in JD':>16}")
    print("-" * 36)
    for word in sorted(result['missing'], key=lambda w: (-job_word_counts[w], w)):
        print(f"{word:<20} {job_word_counts[word]:>16}")

def print_summary_table(valid_results):
    print("\n=== SUMMARY ===")
    print(f"{'Resume File':<28} {'Match %':>8} {'#Matched':>10} {'#Missing':>10}")
    print("-" * 60)
    for r in valid_results:
        print(f"{os.path.basename(r['resume_path']):<28} {r['match_percent']:>8.1f} {r['num_matched']:>10} {r['num_missing']:>10}")

def print_keyword_matrix(all_keywords, valid_results):
    print("\n=== KEYWORD COMPARISON ===")
    header = ["Keyword"] + [os.path.basename(r['resume_path']) for r in valid_results]
    print(" | ".join(f"{col:<15}" for col in header))
    print("-" * (18 * len(header)))
    for word in all_keywords:
        row = [f"{word:<15}"]
        for r in valid_results:
            row.append(f"{r['resume_counts'].get(word, 0):<15}")
        print(" | ".join(row))
    return header  # Useful if you want to reuse in save logic
