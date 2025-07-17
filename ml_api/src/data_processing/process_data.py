from data_loader.load_data import load_data


def process_data():
    data = load_data()
    print(data)


if __name__ == "__main__":
    process_data()
