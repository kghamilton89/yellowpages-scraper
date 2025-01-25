import csv
import sys
from urllib.parse import urlparse
import dns.resolver
from disposable_email_domains import blocklist

# Common email prefixes to try
COMMON_EMAIL_PREFIXES = ['info', 'contact', 'support', 'admin', 'sales', 'hello']

def extract_domain(url):
    """Extract domain from URL and remove subdomains like 'www'."""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc

    # Remove 'www' and other subdomains
    if domain.startswith('www.'):
        domain = domain.split('www.')[1]
    return domain

def generate_emails(domain):
    """Generate common email addresses for a given domain."""
    emails = []
    for prefix in COMMON_EMAIL_PREFIXES:
        emails.append(f"{prefix}@{domain}")
    return emails

def validate_email_with_dns(email):
    """Validate email using DNS checks."""
    try:
        domain = email.split('@')[1]

        # Check MX records for the domain
        mx_records = dns.resolver.resolve(domain, 'MX')
        dns_check = bool(mx_records)  # If MX records exist, DNS check passes

        # Check if the domain is disposable
        is_disposable = domain in blocklist

        return {
            'email': email,
            'dns_check': dns_check,
            'smtp_check': False,  # Skip SMTP validation for now
            'disposable_check': not is_disposable
        }
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        # If no MX records are found or the domain doesn't exist, DNS check fails
        return {
            'email': email,
            'dns_check': False,
            'smtp_check': False,
            'disposable_check': False
        }
    except Exception as e:
        print(f"Error validating email {email}: {e}")
        return {
            'email': email,
            'dns_check': False,
            'smtp_check': False,
            'disposable_check': False
        }

def main(csv_file, limit=None):
    """Main function to process the CSV file."""
    results = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                print(f"Reached limit of {limit} rows. Stopping.")
                break
            website = row['website']
            if not website:
                print(f"Skipping row {i + 1}: No website provided.")
                continue
            domain = extract_domain(website)
            print(f"Processing domain: {domain}")
            emails = generate_emails(domain)
            for email in emails:
                print(f"Validating email: {email}")
                validation_result = validate_email_with_dns(email)
                results.append([
                    validation_result['email'],
                    validation_result['dns_check'],
                    validation_result['smtp_check'],
                    validation_result['disposable_check']
                ])

    # Write results to a new CSV file
    output_file = 'validated_emails.csv'
    print(f"Writing results to {output_file}")
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['email', 'dns_check', 'smtp_check', 'disposable_check'])
        writer.writerows(results)
    print("Script completed successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate.py file.csv [limit]")
        sys.exit(1)

    csv_file = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    try:
        main(csv_file, limit)
    except Exception as e:
        print(f"Script failed with error: {e}")
        sys.exit(1)