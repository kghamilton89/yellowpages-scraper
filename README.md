# Yellow Pages Scraper 2.0

This repository contains a Python-language web scraper for `yellowpages.com` to quickly collect a large amount of user-defined business data using the `requests` library.

Secondarily, there is `validate.py` which uses the enumerated techniques to attempt to build and validate emails for the defined domains. The methodology used is imperfect, but less reputationally damaging that attempting to send real emails.

The code in its current state represents a significant departure from the originally forked library and features the following improvements:

- Graceful handling of `503` HTTP responses caused by implementation of Cloudflare DNS proxying by `yellowpages.com`
- Support for custom multipage content input user-defined start and end page
- Modified input parameter nomenclature and format to support more consistent function
- Retry mechanisms to prevent ungraceful exits, graceful exit processes for continued resource inavailability

Nonetheless, we wish to extend our humble thanks to [ScrapeHero](https://github.com/scrapehero) for providing the foundation upon which this toolkit was created.

## Scraper Script (`scrape.py`)

Yellow Pages Scraper 2.0 extracts the following fields, if they are available:

```python
business_name,
telephone,
rank,
website,
zipcode,
```

`yellowpages.com` does not make business email addresses publically available.

### Scraper Prerequisites

All required libraries are found in `requirements.txt`. Please install them using whichever package manager you prefer.

### Scraper Usage

Yellow Pages web scraper is launched with the following command

```bash
python scrape.py "keyword" "location" x y
```

Where:

- `"keyword"` is the type of business to query
- `"location"` is the human-readable city and state to query
- `x` is the first page to query
- `y` is the last page to query

Thus, a complete request looks like this:

```bash
python scrape.py "restaurant" "Seattle, WA" 1 5
```

The above input queries the first five pages of restaurants in Seattle, Washington.

### Output

The output of Yellow Pages Scraper 2.0 is a comma-separated values (CSV) file named based on the input parameters.

Continuing with the example above, the CSV output is:

`restaurant-seattle-wa-yellowpages.csv`

## Validator Script (`validate.py`)

This Python script reads a CSV file containing website URLs, extracts domains, and attempts to validate email addresses formed by combining a list of common prefixes with each domain. It uses DNS lookups (for MX records), an SMTP handshake, and a disposable email domain check to assess whether an email address is likely valid.

---

### Features

1. **Domain Extraction**  
   - Extracts the domain name from a provided website URL (e.g., removing `http://`, `https://`, `www.`, and additional subdomains).

2. **Common Email Generation**  
   - Generates a set of typical email prefixes (like `info`, `admin`, `sales`, `team`, etc.) to check against each extracted domain.

3. **DNS MX Record Check**  
   - Uses DNS lookups to verify that the domain has valid MX (mail exchange) records.

4. **SMTP Check**  
   - Connects to the domain’s mail server and attempts to verify the existence of the generated email addresses using the `MAIL FROM` and `RCPT TO` commands.

5. **Disposable Email Domain Check**  
   - Compares the domain against a list of known disposable or temporary email providers to mark them as unusable.

6. **CSV Output**  
   - Generates a new CSV file (`validated_emails.csv`) containing the validation results for each attempted email address.

### Validator Prerequisites

- Python 3.x  
- `csv` (built into Python standard library)  
- `smtplib` (built into Python standard library)  
- `socket` (built into Python standard library)  
- `dnspython` for DNS lookups  
- `disposable_email_domains` module containing a blocklist of disposable domains  

You can install these (if not already installed) with:

```bash
pip install dnspython disposable_email_domains
```

### Validator Usage

Run `validate.py` from your command line or terminal. The script accepts at least one argument (the path to a CSV file). An optional second argument can limit the number of rows to be processed:

```bash
python validate.py file.csv [limit]
```

### Arguments

- **file.csv**  
  The path to a CSV file containing at least a `website` column. Each row in the file should have a `website` field with a URL (e.g., `https://www.example.com`, `http://example.org`, or `www.testsite.com`).

- **limit** *(optional)*  
  An integer specifying the maximum number of rows to process. If omitted, the script processes *all* rows in the CSV.

### Example

```bash
python validate.py sample_websites.csv 10
```

In this example, the script processes the first 10 rows from `sample_websites.csv`. For each row:

1. It reads the `website` field.  
2. Extracts the domain name.  
3. Generates a list of common email addresses (e.g., `info@domain.com`, `admin@domain.com`, etc.).  
4. Checks each email address using DNS, SMTP, and a disposable email domain blocklist.  
5. Outputs results to `validated_emails.csv`.

## Validator Output

A file named **`validated_emails.csv`** is created (or overwritten) with the following columns:

- **email**  
  The email address tested (e.g., `info@example.com`).

- **dns_check**  
  `True` if the domain has valid MX records; otherwise `False`.

- **smtp_check**  
  `True` if the mail server accepted `RCPT TO` during the SMTP handshake; otherwise `False`.

- **disposable_check**  
  `True` if the domain is **not** listed as a disposable email domain; `False` indicates it is disposable or could not be checked properly.

A typical output row might look like:

```txt
info@example.com,True,True,True
```

---

## Script Flow

1. **Read CSV**  
   The script opens the provided CSV file and uses `csv.DictReader` to read each row. It expects a column named `website`.

2. **Domain Extraction**  
   For each `website`:  
   - Strips away `http://`, `https://`, and `www.`.  
   - Isolates the primary domain.

3. **Email Generation**  
   Creates a list of emails for common prefixes (e.g., `info@domain.com`, `admin@domain.com`, etc.).

4. **Validation Steps**  
   - **DNS Check**  
     Looks up MX records for the domain. If none are found, `dns_check` is `False`.

   - **SMTP Check**  
     If MX records exist, tries a brief SMTP handshake (`MAIL FROM` / `RCPT TO`). If the server accepts the recipient, `smtp_check` is `True`.

   - **Disposable Check**  
     Compares the domain against a known `blocklist` of disposable email providers. If it appears on the list, `disposable_check` is `False`.

5. **Write Results**  
   Each email is written as a row in `validated_emails.csv` with its associated checks.

---

## Caveats and Notes

- **Rate-Limiting**  
  Some email servers might rate-limit or refuse connections if too many checks occur quickly. Consider adding delays or limiting the number of checks.

- **False Positives/Negatives**  
  - Some mail servers accept all email addresses for a domain (a catch-all policy), causing `smtp_check` to always return `True`.  
  - Other servers might block SMTP verification or use greylisting, resulting in a potential `False` for otherwise valid addresses.

- **Privacy & Compliance**  
  Ensure you are compliant with local regulations when collecting or verifying email addresses.

- **Disposable Email Blocklist**  
  The script relies on a static list of disposable email domains. This list may not be comprehensive or up-to-date.

## Error Handling

- **DNS Exceptions** (`dns.resolver.NoAnswer`, `dns.resolver.NXDOMAIN`, etc.)  
  These exceptions set `dns_check` to `False`, `smtp_check` to `False`, and `disposable_check` to `False`.

- **SMTP Exceptions** (`smtplib.SMTPException`, `socket.error`)  
  The script logs a warning message and sets `smtp_check` to `False` (while leaving `dns_check` as `True` if DNS passed).

- **Generic Exceptions**  
  Any other exceptions result in a failed check for the current email. The script will continue processing subsequent rows.

## Example Run

Given a CSV (`sites.csv`) with:

| website                   |
|---------------------------|
| `https://www.example.com` |
| `http://testsite.org`     |
| `www.nodnsrecord.com`     |

Running:

```bash
python validate.py sites.csv 3
```

Possible `validated_emails.csv` output:

```python
email,dns_check,smtp_check,disposable_check
info@example.com,True,True,True
admin@example.com,True,False,True
support@testsite.org,True,False,True
info@nodnsrecord.com,False,False,True
```

---

## License and Credits

- This script uses [dnspython](https://www.dnspython.org/) for DNS queries.  
- Disposable email domain blocking logic is courtesy of the [disposable_email_domains](https://pypi.org/project/disposable_email_domains/) package.  
- SMTP operations use Python’s built-in `smtplib`.  
- Original code structure for reading CSV and handling logic belongs to this repository.

Feel free to modify or distribute as needed. Ensure compliance with any licensing terms of third-party libraries used.
