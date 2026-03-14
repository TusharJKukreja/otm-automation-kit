# 🚚 OTM Automation Kit – Data Cleaners & Converters

This repository contains Python utilities built to streamline data preparation and transformation for Oracle Transportation Management (OTM), especially in cloud migration and integration scenarios.

All tools are designed to be **client-neutral**, flexible, and reusable across OTM projects.

---

## 📦 Included Tools

### 1. `convert_country_codes.py`  
🔁 **Fixes country code mismatches by converting 2-letter ISO codes to 3-letter ones across CSVs**

- Replaces 2-letter country codes (like `IN`, `US`) with 3-letter ISO codes (`IND`, `USA`) using a standard mapping.
- Dynamically detects columns that contain country codes.
- Handles malformed data safely using `pandas`.
- Preserves special headers used by OTM CSV format.
- Splits large files into smaller batches for upload safety.

---

### 2. `batch_csv_corporation_converter.py`  
📄 **Converts extracted CSVs (from the `Corporation` table) into valid, cleaned OTM XML files**

- Cleans corrupted or HTML-encoded special characters in `GID`/`XID` values.
- Ensures `CORPORATION_XID` doesn’t exceed the 50-character limit after hashcode decoding.
- Uses BeautifulSoup & regex for multi-stage cleanup.
- Generates namespace-compliant XML formatted specifically for `Corporation` objects in OTM.
- Outputs records in batches (e.g., 2000 per file) for stable upload into OTM UI.

---

## 🗂 Folder Structure

```

otm-automation-kit/
├── convert\_country\_codes.py              # Script to clean & convert CSV country codes
├── batch\_csv\_corporation\_converter.py    # Script to convert Corporation CSVs into OTM-ready XML
├── sample\_input/                         # Place your raw CSV files here
├── output\_batches/                       # Cleaned or converted files appear here
└── README.md                             # You're reading it!

````

---

## 🛠 How to Use

### Step 1: Place Files
Place your raw `.csv` files into the `sample_input/` folder.

### Step 2: Edit Script Paths (if needed)
In each script, set your paths like this:

```python
input_folder_path = r"sample_input"
output_folder_path = r"output_batches"
````

### Step 3: Run the Scripts

#### To convert 2-letter to 3-letter country codes:

```bash
python convert_country_codes.py
```

#### To convert Corporation CSVs to cleaned OTM XML:

```bash
python batch_csv_corporation_converter.py
```

---

## 💡 Why These Scripts Matter

* Solves real issues encountered in OTM migrations:

  * Special characters breaking GID/XID length
  * Country code mismatches causing planning & integration errors
* Speeds up remediation by automating fixes across thousands of records
* Supports staging clean data for seamless import into OTM Cloud

---

## 🔐 Disclaimer

These scripts are **generic and reusable** — no client-specific values, credentials, or configurations are embedded.

---

## 🧠 Pro Tips

* Run on test files before using with production data.
* The XML generator script specifically targets the **Corporation** object but can be adapted for others.
* The CSV header format from OTM (usually 3 lines) is preserved for successful UI upload.

---

## 📎 Related Blog Posts

> 🚀 Coming Soon: [OTM Experiences – Issue Logs by Tushar Kukreja](https://coda.io/d/_dqab027IQk2/OTM-Experiences-Document-Issue-Log_su9mEYRz)
> Covers real-world migration issues, solutions, and automation stories.

---

## 🙋‍♂️ Author

**Tushar Kukreja**
OTM Consultant ·
[GitHub](https://github.com/TusharKukreja)

---

## 📄 License

MIT License – Free to use and adapt.

---

## 🤝 Contribute

Pull requests are welcome!
Let’s grow the automation toolkit for OTM together.

```
