import tempfile
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
from loguru import logger

current_path = Path(__file__).parent
COOKIE_DB_CSV = current_path / "csv" / "open-cookie-database.csv"


class CookieDatabase:
    def __init__(self, file=COOKIE_DB_CSV):
        self.file = file
        self.data = None

    def load_from_csv(self) -> dict:
        """Returns a hashtable with cookie data.

        The key is the cookie name and the values contain the cookie data.
        """
        header_names = [
            "id",
            "platform",
            "category",
            "cookie_name",
            "domain",
            "description",
            "retention_period",
            "data_controller",
            "privacy_policy",
            "wildcard_match",
        ]
        index_col = header_names[3]
        df = pd.read_csv(self.file)
        df.columns = pd.Index(header_names)
        df_with_index = df.set_index(index_col, drop=False)
        unique_cookies = df_with_index.drop_duplicates(index_col)
        return unique_cookies.to_dict(orient="index")

    def search(self, cookie_name):
        return self.data.get(cookie_name)

    def __enter__(self):
        self.data = {}
        try:
            self.data = self.load_from_csv()
        except FileNotFoundError:
            logger.error(f"Could not find cookie database '{self.file}'.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def update_database(url=None):
    def user_input():
        print(f"Do you want to update the cookie database? It requests the CSV-file from {url}? [yes/no]: ")
        recv = input()
        if recv != "yes":
            print("Aborting...")
            raise

    def download_file(url):
        print("Downloading cookie database...")
        with urlopen(url) as response:
            return response.read()

    def check_compatibility(csv_file):
        print("Checking compatibility...")
        try:
            with CookieDatabase(csv_file) as cookie_db:
                cookie_db.load_from_csv()
        except Exception:
            raise f"Could not process updated cookie database '{csv_file}'. Keeping old database."

    def write_to_file(binary_data, file):
        with open(file, "wb") as f:
            f.write(binary_data)

    if not url:
        url = "https://github.com/jkwakman/Open-Cookie-Database/raw/master/open-cookie-database.csv"

    user_input()

    # download updated CSV to tmp file
    temp_file = tempfile.NamedTemporaryFile()
    csv_binary = download_file(url)
    with open(temp_file.name, "wb") as f:
        f.write(csv_binary)

        check_compatibility(temp_file.name)
        write_to_file(csv_binary, COOKIE_DB_CSV)  # update CSV
    print(f"Cookie database '{COOKIE_DB_CSV}' updated successfully.")


if __name__ == '__main__':
    update_database()
