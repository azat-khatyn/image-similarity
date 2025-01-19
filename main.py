import argparse
from app.compare import compare_images_hist, compare_images_with_orb


def main():
    # Парсер для аргументов командной строки
    parser = argparse.ArgumentParser(description="Compare two images for similarity.")
    parser.add_argument("img1", type=str, help="Path to the first image.")
    parser.add_argument("img2", type=str, help="Path to the second image.")
    args = parser.parse_args()

    # Запуск сравнения
    similarity_hist = compare_images_hist(args.img1, args.img2)
    similarity_orb = compare_images_with_orb(args.img1, args.img2)
    print(f"Similarity score histogram: {similarity_hist} \n Similarity score ORB: {similarity_orb}")

if __name__ == "__main__":
    main()
