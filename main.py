import argparse
from app.compare import ORBStrategy, HistogramStrategy, PHashStrategy


def main():
    # Парсер для аргументов командной строки
    parser = argparse.ArgumentParser(description="Compare two images for similarity.")
    parser.add_argument("img1", type=str, help="Path to the first image.")
    parser.add_argument("img2", type=str, help="Path to the second image.")
    parser.add_argument(
        "method",
        type=str,
        choices=["orb", "histogram", "phash"],
        help="Comparison method to use (orb, histogram, phash).",
    )
    args = parser.parse_args()

    # Выбор стратегии
    if args.method == "orb":
        strategy = ORBStrategy()
    elif args.method == "histogram":
        strategy = HistogramStrategy()
    elif args.method == "phash":
        strategy = PHashStrategy()
    else:
        raise ValueError(f"Unknown method: {args.method}")

    # Выполнение сравнения
    try:
        similarity_score = strategy.compare(args.img1, args.img2)
        print(f"Similarity score using {args.method}: {similarity_score}")
    except Exception as e:
        print(f"Error during comparison: {e}")

if __name__ == "__main__":
    print("Comparing images ... ", flush=True)
    main()
