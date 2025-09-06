import re
from playwright.sync_api import Page, expect, sync_playwright
import time

def run_test(page: Page):
    # Use a unique username and email for each test run
    unique_id = str(int(time.time()))
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    password = "password123"

    # Navigate to home page
    page.goto("http://127.0.0.1:5000/")

    # Go to Register page
    page.get_by_role("link", name="Register").click()
    expect(page).to_have_url(re.compile(".*register"))

    # Fill out registration form
    page.get_by_label("Username").fill(username)
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_label("Confirm Password").fill(password)
    page.get_by_role("button", name="Sign Up").click()

    # Should be on login page, expect flash message
    expect(page).to_have_url(re.compile(".*login"))
    expect(page.get_by_text("Your account has been created!")).to_be_visible()

    # Fill out login form
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login").click()

    # Should be back on home page, logged in
    expect(page).to_have_url(re.compile(".*"))
    expect(page.get_by_role("link", name="Logout")).to_be_visible()

    # Add first product to cart
    # We target the form associated with the "Laptop" product card
    laptop_card = page.locator(".product-card", has_text="Laptop")
    laptop_card.get_by_role("button", name="Add to Cart").click()

    # Expect flash message
    expect(page.get_by_text('"Laptop" has been added to your cart!')).to_be_visible()

    # Go to cart
    page.get_by_role("link", name=re.compile("Cart")).click()

    # Expect to be on cart page and see the product
    expect(page).to_have_url(re.compile(".*cart"))
    expect(page.get_by_role("heading", name="Shopping Cart")).to_be_visible()
    expect(page.get_by_text("Laptop")).to_be_visible()
    expect(page.get_by_text("Quantity")).to_be_visible()

    # Take screenshot
    page.screenshot(path="jules-scratch/verification/cart_verification.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        run_test(page)
        browser.close()

if __name__ == "__main__":
    main()
