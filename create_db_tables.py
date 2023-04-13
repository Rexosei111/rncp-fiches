from data_model import create_tables, drop_tables

if __name__ == "__main__":
    print("\nDropping db tables...")
    drop_tables()
    print("\nCreating db tables...")
    create_tables()
    print("Done")
