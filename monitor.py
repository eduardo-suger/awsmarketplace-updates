import requests
from bs4 import BeautifulSoup
import difflib
import os

# AWS Marketplace Documentation URLs
URLS = {
    "seller_guide": "https://docs.aws.amazon.com/marketplace/latest/userguide/what-is-marketplace.html",
    "buyer_guide": "https://docs.aws.amazon.com/marketplace/latest/buyerguide/what-is-marketplace.html",
}

# Directory to store documentation snapshots
SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def fetch_documentation(url):
    """Downloads the page content and returns the processed text."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract only visible text
    text = soup.get_text(separator="\n", strip=True)
    return text

def check_for_updates():
    """Checks if the documentation has changed for both Seller and Buyer guides."""
    changes_detected = False

    for guide, url in URLS.items():
        file_path = os.path.join(SNAPSHOT_DIR, f"{guide}.txt")
        new_content = fetch_documentation(url)

        # If no previous snapshot exists, create one
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Reference file created for {guide}. No changes detected yet.")
            continue

        # Read the previously saved content
        with open(file_path, "r", encoding="utf-8") as file:
            old_content = file.read()

        # Compare versions
        if new_content != old_content:
            print(f"🚨 {guide.replace('_', ' ').title()} documentation has changed!")

            # Generate a readable diff
            diff = difflib.unified_diff(
                old_content.splitlines(), new_content.splitlines(), 
                lineterm='', fromfile=f"{guide} (Old)", tofile=f"{guide} (New)"
            )
            diff_text = "\n".join(diff)

            # Save the new version
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)

            # Print the changes
            print(diff_text)

            # Flag that at least one change was detected
            changes_detected = True

    # Commit changes to GitHub if there were any updates
    if changes_detected:
        commit_changes()
    else:
        print("✅ No changes detected in either documentation.")

def commit_changes():
    """Commits changes to GitHub."""
    os.system("git add snapshots/")
    os.system('git commit -m "Updated AWS Marketplace documentation snapshots"')
    os.system("git push")

# Run the check
check_for_updates()
