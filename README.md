# Idioms Dictionary Database (成語典)

This project contains a local SQLite database of idioms scraped from the [Ministry of Education's Dictionary of Idioms (教育部成語典)](https://dict.idioms.moe.edu.tw/bookView.jsp?ID=-1).

## Project Structure

- `idioms.db`: The SQLite database containing the scraped idioms.
- `scrape_idioms.py`: The Python script used to crawl and parse the phonetic index.
- `README.md`: This documentation file.

## Database Schema

The database `idioms.db` contains a table named `idioms` with the following columns:

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary key (auto-increment) |
| `name` | TEXT | The name of the idiom (Chinese characters) |
| `phonetic_initial` | TEXT | The Bopomofo initial (ㄅ, ㄆ, ㄇ, etc.) |
| `external_id` | TEXT | The unique ID assigned by the original website |
| `is_main_entry` | BOOLEAN | `1` if it's a primary entry, `0` if it's a variant |

## Usage Examples

You can query the database using any SQLite client or the command line.

### 1. Count Total Entries
```bash
sqlite3 idioms.db "SELECT COUNT(*) FROM idioms;"
```

### 2. List Idioms by Phonetic Initial (e.g., 'ㄅ')
```bash
sqlite3 idioms.db "SELECT name FROM idioms WHERE phonetic_initial = 'ㄅ' LIMIT 10;"
```

### 3. Summary of Entries per Phonetic Group
```bash
sqlite3 idioms.db "SELECT phonetic_initial, COUNT(*) FROM idioms GROUP BY phonetic_initial ORDER BY id;"
```

### 4. Search for an Idiom by Name
```bash
sqlite3 idioms.db "SELECT * FROM idioms WHERE name LIKE '%畫蛇添足%';"
```

## Maintenance

To refresh the database, ensure you have `requests` and `beautifulsoup4` installed, then run:

```bash
python3 scrape_idioms.py
```

---
*Note: This data is for educational and personal use. Please respect the Ministry of Education's terms of service regarding automated scraping.*
