from app.services.ingestion import build_index


if __name__ == "__main__":
    count = build_index()
    print(f"Index warm-up complete with {count} retrieved chunks.")
