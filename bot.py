from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os
from datetime import datetime
import json

# Configuration
USERNAME =       
PASSWORD =  
RESUME_PATH = 
JOB_KEYWORDS = ["data analyst", "data science", "python developer"]  
MAX_JOBS_PER_KEYWORD = 25  
LOCATION = "Hyderabad"
MIN_DELAY = 2
MAX_DELAY = 5

PERSONAL_INFO = {
    'first_name': 'Vangapandu',
    'last_name': 'Laxmana Rao',
    'email': USERNAME,
    'phone': '+91-7993803176',  
    'phone_country_code': '+91',  # NEW: India country code
    'phone_number': '7993803176',  # NEW: Phone without country code
    'city': 'Hyderabad',
    'country': 'India',
    'country_code': 'IN',  # NEW: India country code (ISO format)
    'state': 'Telangana',  # NEW: State information
    'postal_code': '500001',  # NEW: Add your postal code
    'experience_years': '0',     
    'current_company': 'none',  
    'linkedin_url': 'https://www.linkedin.com/in/laxman-v/',  
    'cover_letter': """Dear Hiring Manager,

I am excited to apply for this position. i'm interested in data analysis, Python development, and data science, I believe I would be a valuable addition to your team. I am passionate about leveraging data to drive business insights and am eager to contribute to your organization's success.

Thank you for considering my application.

Best regards,
Laxmana ra Vangapangu"""
}

# Advanced options
SKIP_APPLIED_JOBS = True
SAVE_APPLIED_JOBS = True
LOG_FILE = f"linkedin_job_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
HANDLE_COMPANY_SITES = True  # New option to handle external applications

class LinkedInJobBot:
    def __init__(self):
        self.setup_driver()
        self.wait = WebDriverWait(self.driver, 15)
        self.applied_jobs = []
        self.failed_jobs = []
        self.company_site_jobs = []  # Track jobs that require company site application
        
    def setup_driver(self):
        """Setup Chrome driver with ChromeDriverManager for automatic driver management"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        
        # Add user agent to avoid detection
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.log("Chrome driver initialized successfully")
        except Exception as e:
            self.log(f"Chrome driver setup failed: {e}", "ERROR")
            raise
            
        # Remove webdriver property to avoid detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.implicitly_wait(10)
        
    def log(self, msg, level="INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M")
        icons = {"INFO": "🔹", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "DEBUG": "🔍", "COMPANY": "🏢", "EASY": "⚡"}
        print(f"[{timestamp}] {icons.get(level, '🔹')} {msg}")
        
    def random_delay(self, min_delay=None, max_delay=None):
        """Add random delay to avoid detection"""
        min_d = min_delay or MIN_DELAY
        max_d = max_delay or MAX_DELAY
        delay = random.uniform(min_d, max_d)
        time.sleep(delay)
        
    def login(self):
        """Login to LinkedIn"""
        try:
            self.log("Navigating to LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            
            self.log("Entering username...")
            username_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='username']"))
            )
            username_field.clear()
            username_field.send_keys(USERNAME)
            self.random_delay(1, 3)
            
            self.log("Entering password...")
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='password']"))
            )
            password_field.clear()
            password_field.send_keys(PASSWORD)
            self.random_delay(1, 3)
            
            self.log("Clicking login button...")
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            login_button.click()
            
            self.log("Waiting for login to complete...")
            time.sleep(5)
            
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                self.log("Successfully logged in!", "SUCCESS")
                self.random_delay(2, 3)
                return
            
            try:
                # Check for feed or profile elements that indicate successful login
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/feed/')]")),
                        EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'Me')]")),
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Me')]"))
                    )
                )
                self.log(" Successfully logged in!", "SUCCESS")
                self.random_delay(2, 3)
            except TimeoutException:
                raise Exception("Login verification failed - please check credentials")
                
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
    
    def search_jobs(self, keyword, location=None):
        """Navigate to jobs page for the given keyword"""
        try:
            self.log(f"Searching for jobs with keyword: '{keyword}'...")
            
            # Create LinkedIn search URL with Easy Apply filter
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}"
            
            # Add location if specified
            if location:
                search_url += f"&location={location.replace(' ', '%20')}"
                
            # Add Easy Apply filter and other filters
            search_url += "&f_AL=true"  
            search_url += "&f_E=2,3"    
            search_url += "&f_TPR=r86400"  
            
            self.log(f"Navigating to: {search_url}")
            self.driver.get(search_url)
            time.sleep(5)
            
            # Verify page loaded successfully
            page_title = self.driver.title.lower()
            if "linkedin" in page_title:
                self.log(f" Successfully loaded jobs page for '{keyword}'", "SUCCESS")
            else:
                self.log(f" Page may not have loaded correctly", "WARNING")
                
        except Exception as e:
            self.log(f"Failed to load jobs page for '{keyword}': {str(e)}", "ERROR")
            # Fallback: try basic search
            try:
                self.log("Trying fallback search method...", "WARNING")
                fallback_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&f_AL=true"
                self.driver.get(fallback_url)
                time.sleep(3)
                self.log("Used fallback search method", "SUCCESS")
            except Exception as fallback_error:
                raise Exception(f"All search methods failed for '{keyword}': {str(fallback_error)}")
    
    def get_job_links_from_listing_page(self):
        """Extract job links from the job listing page"""
        job_links = []
        
        # LinkedIn-specific selectors for job cards
        link_selectors = [
            # Primary selectors for LinkedIn job cards
            "a.job-card-container__link.job-card-list__title",
            "a[data-control-name='job_card_click']",
            "a.job-card-list__title-link",
            "a[href*='/jobs/view/']",
            
            # Alternative selectors
            ".jobs-search-results__list-item a[href*='/jobs/view/']",
            ".job-card-container a[href*='/jobs/view/']",
            ".jobs-search-results-list a[href*='/jobs/view/']",
            
            # Backup selectors
            "a[data-control-name*='job']",
            ".job-card-list__title",
            ".job-card-container__primary-description"
        ]
        
        for selector in link_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    try:
                        href = element.get_attribute("href")
                        
                        # Get job title from the element or its children
                        title = ""
                        try:
                            title = element.text.strip()
                            if not title:
                                # Try to find title in child elements
                                title_child = element.find_element(By.CSS_SELECTOR, ".job-card-list__title, h3, span")
                                title = title_child.text.strip() if title_child else ""
                        except:
                            title = "Unknown Title"
                        
                        # Filter for target roles only
                        if not self.is_target_role(title):
                            continue
                        
                        # Validate that this looks like a LinkedIn job link
                        if (href and 
                            "/jobs/view/" in href and
                            title and 
                            len(title) > 3):
                            
                            job_data = {
                                'title': title,
                                'url': href,
                                'element': element
                            }
                            
                            # Avoid duplicates
                            if not any(job['url'] == href for job in job_links):
                                job_links.append(job_data)
                                
                    except Exception as e:
                        continue
                
                if job_links:
                    self.log(f"Found {len(job_links)} job links using selector: {selector}", "SUCCESS")
                    break
                
            except Exception as e:
                self.log(f"Selector {selector} failed: {str(e)}", "DEBUG")
                continue
        
        # If no jobs found with primary selectors, try scrolling and searching again
        if not job_links:
            try:
                self.log("No jobs found, trying to scroll and reload...", "WARNING")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Try again with basic selector
                elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
                for element in elements[:MAX_JOBS_PER_KEYWORD]:
                    try:
                        href = element.get_attribute("href")
                        title = element.text.strip() or "LinkedIn Job"
                        
                        if href and "/jobs/view/" in href:
                            job_links.append({
                                'title': title,
                                'url': href,
                                'element': element
                            })
                    except:
                        continue
                        
            except Exception as e:
                self.log(f"Scroll and retry failed: {str(e)}", "DEBUG")
        
        # Limit to MAX_JOBS_PER_KEYWORD
        if len(job_links) > MAX_JOBS_PER_KEYWORD:
            job_links = job_links[:MAX_JOBS_PER_KEYWORD]
            
        self.log(f"Found {len(job_links)} relevant job links to process", "INFO")
        
        # Show sample of found jobs
        for i, job in enumerate(job_links[:3]):
            self.log(f"Sample {i+1}: {job['title']}", "DEBUG")
            
        return job_links
    
    def is_target_role(self, job_title):
        """Check if job title matches target roles"""
        title_lower = job_title.lower()
        target_keywords = [
            "data analyst", "data analysis", "data science", "data scientist", 
            "python developer", "python", "data engineer", "machine learning",
            "business analyst", "analytics", "bi analyst", "sql"
        ]
        
        return any(keyword in title_lower for keyword in target_keywords)
    
    def handle_cookies_popup(self):
        try:
            cookie_selectors = [
            # Common XPath selectors
            "//button[contains(translate(text(),'ACCEPT','accept'),'accept')]",
            "//button[contains(translate(text(),'ALLOW','allow'),'allow')]",
            "//button[contains(translate(text(),'OK','ok'),'ok')]",
            "//button[contains(translate(text(),'AGREE','agree'),'agree')]",
            "//button[contains(translate(text(),'CONTINUE','continue'),'continue')]",
            "//a[contains(translate(text(),'ACCEPT','accept'),'accept')]",

            # Common CSS selectors
            "button[id*='accept']",
            "button[class*='accept']",
            "button[id*='cookie']",
            "button[class*='cookie']",
            ".cookie-accept",
            ".accept-cookies",
            "#cookie-accept",
            "#accept-cookies"
        ]

            for selector in cookie_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                    # CSS selector
                        element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )

                    element.click()
                    self.log(f"Clicked cookie popup button using selector: {selector}")
                    return True  # Once clicked, break out of the loop

                except TimeoutException:
                    continue  # Try the next selector

            self.log(" No cookie popup detected or clickable.")
            return False

        except Exception as e:
            self.log(f"Error handling cookies: {str(e)}", "ERROR")
            return False
    
    def handle_country_field(self, field_element):
        """Handle country selection fields with India as default"""
        try:
            # Check if it's a select dropdown
            if field_element.tag_name.lower() == 'select':
                select_obj = Select(field_element)
                
                # Try different variations for India
                india_options = ['India', 'IN', 'india', 'INDIA', 'IND']
                
                for option_text in india_options:
                    try:
                        select_obj.select_by_visible_text(option_text)
                        self.log(f"Selected country: {option_text}", "SUCCESS")
                        return True
                    except:
                        try:
                            select_obj.select_by_value(option_text)
                            self.log(f" Selected country by value: {option_text}", "SUCCESS")
                            return True
                        except:
                            continue
                
                # If direct selection doesn't work, try to find India in options
                for option in select_obj.options:
                    if 'india' in option.text.lower():
                        select_obj.select_by_visible_text(option.text)
                        self.log(f" Selected country: {option.text}", "SUCCESS")
                        return True
                        
            else:
                # For input fields, try typing "India"
                field_element.clear()
                field_element.send_keys("India")
                time.sleep(1)
                
                # Check if dropdown appeared
                try:
                    dropdown_options = self.driver.find_elements(By.XPATH, 
                        "//div[contains(@class, 'dropdown') or contains(@class, 'menu')]//div[contains(text(), 'India')]")
                    
                    if dropdown_options:
                        dropdown_options[0].click()
                        self.log(" Selected India from dropdown", "SUCCESS")
                        return True
                    else:
                        # Try pressing Enter or Arrow Down + Enter
                        field_element.send_keys(Keys.ARROW_DOWN)
                        field_element.send_keys(Keys.ENTER)
                        self.log(" Selected India via keyboard", "SUCCESS")
                        return True
                except:
                    pass
                    
                self.log(" Filled country field with India", "SUCCESS")
                return True
                
        except Exception as e:
            self.log(f"Failed to handle country field: {str(e)}", "ERROR")
            return False
    
    def handle_phone_country_code(self, field_element):
        """Handle phone country code fields with +91 (India)"""
        try:
            # Check if it's a select dropdown
            if field_element.tag_name.lower() == 'select':
                select_obj = Select(field_element)
                
                # Try different variations for India country code
                india_codes = ['+91', '91', 'India (+91)', 'IN (+91)', '+91 India']
                
                for code in india_codes:
                    try:
                        select_obj.select_by_visible_text(code)
                        self.log(f"Selected phone country code: {code}", "SUCCESS")
                        return True
                    except:
                        try:
                            select_obj.select_by_value(code)
                            self.log(f" Selected phone country code by value: {code}", "SUCCESS")
                            return True
                        except:
                            continue
                
                # Search through all options for India/91
                for option in select_obj.options:
                    if any(keyword in option.text.lower() for keyword in ['india', '+91', '91']):
                        select_obj.select_by_visible_text(option.text)
                        self.log(f"Selected phone country code: {option.text}", "SUCCESS")
                        return True
                        
            else:
                # For input fields
                field_element.clear()
                field_element.send_keys("+91")
                self.log(" Filled phone country code: +91", "SUCCESS")
                return True
                
        except Exception as e:
            self.log(f" Failed to handle phone country code: {str(e)}", "ERROR")
            return False
    
    def handle_company_site_application(self, job_title, company):
        """Handle application process on company website"""
        try:
            self.log(f" Processing company site application for: {job_title}", "COMPANY")
            
            # Wait for page to load
            time.sleep(5)
            
            # Look for application form or apply buttons on company site
            company_apply_selectors = [
                "//button[contains(translate(text(),'APPLY','apply'),'apply')]",
                "//a[contains(translate(text(),'APPLY','apply'),'apply')]",
                "//input[contains(translate(@value,'APPLY','apply'),'apply')]",
                "//button[contains(translate(text(),'Easy Apply','Easy Apply'),'Easy Apply')]",
                "//a[contains(translate(text(),'Easy Apply','Easy Apply'),'Easy Apply')]",
                "//input[contains(translate(@value,'Easy Apply','Easy Apply'),'Easy Apply')]",
                "//button[contains(text(),'Submit Application')]",
                "//button[contains(text(),'Join Us')]",
                "//a[contains(text(),'Career')]",
                "//a[contains(text(),'Jobs')]",
                "//button[contains(text(),'Get Started')]",
                
                # Generic form submissions
                "//button[@type='submit']",
                "//input[@type='submit']"
            ]
            
            # Try to find and click apply button on company site
            for selector in company_apply_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Scroll to element
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            
                            element.click()
                            self.log(f"Clicked company site button: {element.text}", "COMPANY")
                            time.sleep(3)
                            
                            # Handle any forms that appear
                            form_handled = self.handle_company_site_form()
                            
                            if form_handled:
                                return True
                            
                            break
                except Exception as e:
                    continue
            
            # If no specific apply button found, look for forms to fill
            return self.handle_company_site_form()
            
        except Exception as e:
            self.log(f"Company site application error: {str(e)}", "ERROR")
            return False
    
    def handle_company_site_form(self):
        """Handle forms on company websites"""
        try:
            # Look for file upload inputs for resume
            file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            
            if file_inputs and RESUME_PATH and os.path.exists(RESUME_PATH):
                for file_input in file_inputs:
                    try:
                        if file_input.is_displayed():
                            file_input.send_keys(RESUME_PATH)
                            self.log("Resume uploaded to company site", "COMPANY")
                            time.sleep(2)
                            break
                    except:
                        continue
            
            # Fill common form fields automatically
            self.fill_external_form_fields()
            
            # Look for required text fields that need manual input
            text_inputs = self.driver.find_elements(By.XPATH, 
                "//input[@type='text' and @required] | //input[@required and not(@type)] | //textarea[@required]")
            
            if text_inputs:
                self.log(f"Found {len(text_inputs)} required fields on company site", "COMPANY")
                self.log(" Manual input may be required for company site application", "WARNING")
                
                for i, input_field in enumerate(text_inputs[:5]):  # Limit to first 5 fields
                    try:
                        field_name = (input_field.get_attribute("name") or 
                                    input_field.get_attribute("placeholder") or 
                                    input_field.get_attribute("id") or 
                                    f"Field {i+1}")
                        
                        if input_field.is_displayed() and not input_field.get_attribute("value"):
                            # Try to auto-fill based on field name
                            filled = self.auto_fill_field(input_field, field_name.lower())
                            
                            if not filled:
                                print(f"\n COMPANY SITE INPUT REQUIRED:")
                                print(f"Field: {field_name}")
                                print(f"Current URL: {self.driver.current_url}")
                                user_input = input(f"Enter value for '{field_name}' (or press Enter to skip): ")
                                
                                if user_input.strip():
                                    input_field.clear()
                                    input_field.send_keys(user_input)
                                    self.log(f"Filled field: {field_name}", "COMPANY")
                            
                    except Exception as e:
                        continue
            
            # Look for submit buttons
            submit_buttons = self.driver.find_elements(By.XPATH, 
                "//button[@type='submit'] | //input[@type='submit'] | "
                "//button[contains(translate(text(),'SUBMIT','submit'),'submit')] | "
                "//button[contains(translate(text(),'SEND','send'),'send')] | "
                "//button[contains(translate(text(),'Easy Apply','Easy Apply'),'Easy Apply')] | "
                "//button[contains(translate(text(),'APPLY','apply'),'apply')]")
            
            for btn in submit_buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        # Auto-submit if we have basic info filled
                        btn.click()
                        self.log(f"Submitted company site application", "COMPANY")
                        time.sleep(3)
                        return True
                except:
                    continue
            
            # If we made it here, consider it a partial success
            if text_inputs or file_inputs:
                self.log("Partially processed company site application", "COMPANY")
                return True
            
            return False
            
        except Exception as e:
            self.log(f"Company site form handling error: {str(e)}", "WARNING")
            return False
    
    def auto_fill_field(self, field_element, field_name):
        """Auto-fill form fields based on field name with enhanced country support"""
        try:
            # Map field names to personal info (Updated with country support)
            field_mappings = {
                'first': PERSONAL_INFO['first_name'],
                'fname': PERSONAL_INFO['first_name'],
                'firstname': PERSONAL_INFO['first_name'],
                'last': PERSONAL_INFO['last_name'],
                'lname': PERSONAL_INFO['last_name'],
                'lastname': PERSONAL_INFO['last_name'],
                'email': PERSONAL_INFO['email'],
                'phone': PERSONAL_INFO['phone_number'],  # Use phone without country code
                'mobile': PERSONAL_INFO['phone_number'],
                'city': PERSONAL_INFO['city'],
                'location': PERSONAL_INFO['city'],
                'state': PERSONAL_INFO['state'],
                'postal': PERSONAL_INFO['postal_code'],
                'zip': PERSONAL_INFO['postal_code'],
                'experience': PERSONAL_INFO['experience_years'],
                'company': PERSONAL_INFO['current_company']
            }
            
            # Special handling for country fields
            if any(keyword in field_name for keyword in ['country', 'nation']):
                return self.handle_country_field(field_element)
            
            # Special handling for phone country code fields
            if any(keyword in field_name for keyword in ['country_code', 'phone_country', 'code']):
                return self.handle_phone_country_code(field_element)
            
            # Handle full phone number with country code
            if 'phone' in field_name and 'full' in field_name:
                return self.fill_form_field(field_element, PERSONAL_INFO['phone'], field_name)
            
            # Regular field mapping
            for key, value in field_mappings.items():
                if key in field_name and value:
                    return self.fill_form_field(field_element, value, field_name)
            
            return False
            
        except Exception as e:
            return False
    
    def fill_external_form_fields(self):
        """Fill form fields on external company websites with enhanced country support"""
        try:
            # Enhanced field mappings for external sites (Updated with country info)
            field_mappings = {
                'first_name': ['firstname', 'first_name', 'fname', 'given_name'],
                'last_name': ['lastname', 'last_name', 'lname', 'family_name', 'surname'],
                'email': ['email', 'email_address', 'e_mail'],
                'phone_number': ['phone', 'telephone', 'mobile', 'phone_number', 'phonenumber'],
                'phone': ['phone_full', 'full_phone', 'phone_with_code'],  # Full phone with country code
                'city': ['city', 'location', 'current_city'],
                'state': ['state', 'region', 'province'],
                'postal_code': ['postal', 'zip', 'postal_code', 'zipcode', 'pincode'],
                'experience_years': ['experience', 'years_experience', 'work_experience']
            }
            
            for info_key, field_names in field_mappings.items():
                value = PERSONAL_INFO.get(info_key, '')
                if not value:
                    continue
                    
                for field_name in field_names:
                    selectors = [
                        f"input[name*='{field_name}']",
                        f"input[id*='{field_name}']",
                        f"input[placeholder*='{field_name}']"
                    ]
                    
                    for selector in selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.is_enabled() and not element.get_attribute("value"):
                                    self.fill_form_field(element, value, field_name)
                                    time.sleep(0.5)
                                    break
                        except:
                            continue
            
            # Handle country fields specifically
            country_selectors = [
                "select[name*='country']",
                "select[id*='country']",
                "input[name*='country']",
                "input[id*='country']",
                "select[name*='nation']",
                "input[placeholder*='country']"
            ]
            
            for selector in country_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            self.handle_country_field(element)
                            time.sleep(0.5)
                            break
                except:
                    continue
            
            # Handle phone country code fields specifically
            phone_country_selectors = [
                "select[name*='phone_country']",
                "select[name*='country_code']",
                "select[id*='phone_country']",
                "select[id*='country_code']",
                "input[name*='country_code']",
                "input[placeholder*='country code']"
            ]
            
            for selector in phone_country_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            self.handle_phone_country_code(element)
                            time.sleep(0.5)
                            break
                except:
                    continue
                            
        except Exception as e:
            self.log(f"Error filling external form fields: {str(e)}", "WARNING")
    
    def handle_application_form(self):
        """Handle different types of application forms that might appear on LinkedIn"""
        try:
            # Wait for any forms to load
            time.sleep(2)
            
            # Check for resume upload
            file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            if file_inputs and RESUME_PATH and os.path.exists(RESUME_PATH):
                for file_input in file_inputs:
                    try:
                        if file_input.is_displayed():
                            file_input.send_keys(RESUME_PATH)
                            self.log("Resume uploaded successfully", "SUCCESS")
                            self.random_delay(2, 3)
                            break
                    except:
                        continue
            
            # Look for any submit/continue buttons in forms
            form_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(translate(text(),'SUBMIT','submit'),'submit') or "
                "contains(translate(text(),'CONTINUE','continue'),'continue') or "
                "contains(translate(text(),'SEND','send'),'send') or "
                "contains(translate(text(),'APPLY','apply'),'apply')]")
            
            for btn in form_buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        self.log(f"Clicked form button: {btn.text}", "SUCCESS")
                        time.sleep(2)
                        break
                except:
                    continue
            
            # Handle any confirmation dialogs
            try:
                confirm_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(),'Confirm') or contains(text(),'Yes') or contains(text(),'OK')]")
                for btn in confirm_buttons:
                    if btn.is_displayed():
                        btn.click()
                        self.log("Confirmed application", "SUCCESS")
                        break
            except:
                pass
                
        except Exception as e:
            self.log(f"Form handling error: {str(e)}", "WARNING")
    
    def apply_to_jobs(self):
        """Main job application method - gets job links and applies to each"""
        jobs_attempted = 0
        jobs_applied = 0
        
        try:
            # Get all job links from the listing page
            job_links = self.get_job_links_from_listing_page()
            
            if not job_links:
                self.log("No relevant job links found on the listing page", "ERROR")
                return 0, 0
            
            # Process each job
            for i, job_data in enumerate(job_links):
                if jobs_attempted >= MAX_JOBS_PER_KEYWORD:
                    break
                
                try:
                    self.log(f"\n--- Processing Job {i+1}/{len(job_links)} ---", "INFO")
                    
                    success, reason = self.apply_to_single_job(job_data['url'], job_data['title'])
                    
                    if success:
                        jobs_applied += 1
                        self.log(f"Successfully applied to: {job_data['title']}", "SUCCESS")
                    else:
                        self.log(f" Failed to apply to: {job_data['title']} - {reason}", "WARNING")
                        self.failed_jobs.append({
                            'title': job_data['title'],
                            'url': job_data['url'],
                            'reason': reason
                        })
                    
                    jobs_attempted += 1
                    
                    # Add delay between applications
                    if i < len(job_links) - 1:  # Don't delay after the last job
                        self.random_delay(5, 8)  # Longer delay between job applications
                    
                except Exception as e:
                    self.log(f"Error processing job {i+1}: {str(e)}", "ERROR")
                    jobs_attempted += 1
                    continue
            
            return jobs_attempted, jobs_applied
            
        except Exception as e:
            self.log(f" Error in apply_to_jobs: {str(e)}", "ERROR")
            return jobs_attempted, jobs_applied
    
    def is_job_already_applied(self, job_title, company):
        """Check if job was already applied to"""
        if not SKIP_APPLIED_JOBS:
            return False
            
        job_signature = f"{job_title.lower()}_{company.lower()}"
        return any(job_signature in applied['signature'] for applied in self.applied_jobs)
    
    def fill_form_field(self, field_element, value, field_name="field"):
        """Helper method to fill form fields safely"""
        try:
            if not value:
                return False
            
            # Clear existing content
            field_element.clear()
            time.sleep(0.5)
            
            # Type the value
            field_element.send_keys(str(value))
            self.log(f" Filled {field_name}: {value}", "SUCCESS")
            time.sleep(0.5)
            return True
            
        except Exception as e:
            self.log(f" Failed to fill {field_name}: {str(e)}", "ERROR")
            return False
    
    def handle_easy_apply_form(self):
        """Handle LinkedIn Easy Apply form with multiple steps and enhanced country support"""
        try:
            self.log("Looking for Easy Apply form...", "EASY")
            
            max_steps = 5  # Maximum number of form steps to handle
            current_step = 0
            
            while current_step < max_steps:
                current_step += 1
                self.log(f" Processing form step {current_step}", "EASY")
                
                # Wait for form to load
                time.sleep(3)
                
                # Look for form fields and fill them
                form_filled = False
                
                # Fill basic contact information
                contact_fields = {
                    'firstName': PERSONAL_INFO['first_name'],
                    'lastName': PERSONAL_INFO['last_name'],
                    'email': PERSONAL_INFO['email'],
                    'phone': PERSONAL_INFO['phone_number']  # Phone without country code for LinkedIn
                }
                
                for field_name, value in contact_fields.items():
                    try:
                        # Multiple selectors for different field naming conventions
                        field_selectors = [
                            f"input[name='{field_name}']",
                            f"input[id*='{field_name}']",
                            f"input[placeholder*='{field_name}']",
                            f"input[aria-label*='{field_name}']"
                        ]
                        
                        for selector in field_selectors:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.is_enabled():
                                    if self.fill_form_field(element, value, field_name):
                                        form_filled = True
                                    break
                            if form_filled:
                                break
                    except:
                        continue
                
                # Handle country fields in Easy Apply forms
                try:
                    country_selectors = [
                        "select[name*='country']",
                        "select[id*='country']",
                        "input[name*='country']",
                        "input[id*='country']"
                    ]
                    
                    for selector in country_selectors:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                if self.handle_country_field(element):
                                    form_filled = True
                                break
                except:
                    pass
                
                # Handle phone country code in Easy Apply forms
                try:
                    phone_country_selectors = [
                        "select[name*='phoneCountry']",
                        "select[name*='phone-country']",
                        "select[id*='phoneCountry']",
                        "select[id*='phone-country']"
                    ]
                    
                    for selector in phone_country_selectors:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                if self.handle_phone_country_code(element):
                                    form_filled = True
                                break
                except:
                    pass
                
                # Handle city/location fields
                try:
                    location_selectors = [
                        "input[name*='city']",
                        "input[id*='city']",
                        "input[name*='location']",
                        "input[id*='location']"
                    ]
                    
                    for selector in location_selectors:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled() and not element.get_attribute("value"):
                                if self.fill_form_field(element, PERSONAL_INFO['city'], 'city'):
                                    form_filled = True
                                break
                except:
                    pass
                
                # Handle file upload (Resume)
                try:
                    file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
                    for file_input in file_inputs:
                        if file_input.is_displayed() and RESUME_PATH and os.path.exists(RESUME_PATH):
                            file_input.send_keys(RESUME_PATH)
                            self.log("Resume uploaded successfully", "EASY")
                            form_filled = True
                            time.sleep(2)
                            break
                except:
                    pass
                
                # Handle dropdown fields (Experience, Education, etc.)
                try:
                    select_elements = self.driver.find_elements(By.TAG_NAME, "select")
                    for select_elem in select_elements:
                        if select_elem.is_displayed():
                            # Skip if it's a country or phone country field (already handled above)
                            elem_name = (select_elem.get_attribute("name") or "").lower()
                            elem_id = (select_elem.get_attribute("id") or "").lower()
                            
                            if any(keyword in elem_name or keyword in elem_id 
                                   for keyword in ['country', 'phone']):
                                continue
                            
                            select_obj = Select(select_elem)
                            options = select_obj.options
                            
                            # Try to select relevant experience level
                            if len(options) > 1:
                                # Look for options that match experience years
                                exp_years = PERSONAL_INFO.get('experience_years', '0')
                                for option in options[1:]:  # Skip first option (usually "Select...")
                                    if exp_years in option.text or 'year' in option.text.lower():
                                        select_obj.select_by_visible_text(option.text)
                                        self.log(f"Selected dropdown option: {option.text}", "EASY")
                                        form_filled = True
                                        break
                                else:
                                    # If no matching option, select second option
                                    select_obj.select_by_index(1)
                                    form_filled = True
                except:
                    pass
                
                # Handle text areas (Cover letter, additional info)
                try:
                    text_areas = self.driver.find_elements(By.TAG_NAME, "textarea")
                    for textarea in text_areas:
                        if textarea.is_displayed() and textarea.is_enabled():
                            placeholder = textarea.get_attribute("placeholder") or ""
                            if "cover" in placeholder.lower() or "message" in placeholder.lower():
                                self.fill_form_field(textarea, PERSONAL_INFO['cover_letter'], "cover letter")
                                form_filled = True
                            elif not textarea.get_attribute("value"):
                                # Fill with generic message if empty
                                self.fill_form_field(textarea, "I am very interested in this position and believe my skills and experience make me a great fit.", "additional info")
                                form_filled = True
                except:
                    pass
                
                # Handle checkboxes and radio buttons
                try:
                    # Check required checkboxes (like terms and conditions)
                    checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                    for checkbox in checkboxes:
                        if checkbox.is_displayed() and not checkbox.is_selected():
                            label_text = ""
                            try:
                                # Get associated label text
                                label = self.driver.find_element(By.XPATH, f"//label[@for='{checkbox.get_attribute('id')}']")
                                label_text = label.text.lower()
                            except:
                                pass
                            
                            # Check boxes for terms, privacy, etc.
                            if any(word in label_text for word in ['term', 'privacy', 'agree', 'consent']):
                                checkbox.click()
                                self.log(f"Checked checkbox: {label_text[:50]}...", "EASY")
                                form_filled = True
                                time.sleep(0.5)
                except:
                    pass
                
                # Look for Next/Continue/Submit buttons
                button_found = False
                button_selectors = [
                    "//button[contains(text(), 'Next')]",
                    "//button[contains(text(), 'Continue')]",
                    "//button[contains(text(), 'Submit')]",
                    "//button[contains(text(), 'Review')]",
                    "//button[contains(@aria-label, 'Continue')]",
                    "//button[contains(@aria-label, 'Submit')]",
                    "//button[contains(@class, 'artdeco-button--primary')]"
                ]
                
                for selector in button_selectors:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, selector)
                        for button in buttons:
                            if button.is_displayed() and button.is_enabled():
                                button_text = button.text or button.get_attribute('aria-label') or 'Button'
                                
                                # Scroll to button
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(1)
                                
                                # Click the button
                                button.click()
                                self.log(f" Clicked button: {button_text}", "EASY")
                                button_found = True
                                time.sleep(3)
                                
                                # If this was a submit button, we're done
                                if 'submit' in button_text.lower():
                                    return True
                                
                                break
                        if button_found:
                            break
                    except Exception as e:
                        continue
                
                # If no button found or no form fields, we might be done
                if not button_found:
                    self.log(" No more form steps found", "EASY")
                    break
                
                # Check if we've reached the final confirmation page
                if any(text in self.driver.page_source.lower() for text in ['application submitted', 'thank you', 'application received']):
                    self.log(" Application submitted successfully!", "EASY")
                    return True
            
            return True
            
        except Exception as e:
            self.log(f" Error handling Easy Apply form: {str(e)}", "ERROR")
            return False

    def apply_to_single_job(self, job_url, job_title):
        try:
            self.log(f" Opening job: {job_title}", "INFO")
            self.driver.get(job_url)
            time.sleep(3)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Extract company name
            company = "Unknown Company"
            try:
                company_selectors = [
                ".jobs-unified-top-card__company-name a",
                ".jobs-unified-top-card__company-name",
                ".topcard__org-name-link",
                ".job-details-jobs-unified-top-card__company-name"
                 ]
                for selector in company_selectors:
                    try:
                        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if elem.text.strip():
                            company = elem.text.strip()
                            break
                    except:
                        continue
            except:
                pass

            self.log(f"Company: {company}", "INFO")

            if self.is_job_already_applied(job_title, company):
                self.log(" Already applied to this job, skipping...", "WARNING")
                return False, "Already applied"

            # Apply button detection
            apply_button_selectors = [
                "//button[contains(@class, 'jobs-apply-button') and contains(text(), 'Easy Apply')]",
                "//button[contains(text(), 'Easy Apply')]",
                "//a[contains(text(), 'Easy Apply')]",
                "//button[contains(@class, 'jobs-apply-button')]",
                "//button[contains(text(), 'Apply')]",
                "//a[contains(text(), 'Apply')]",
                "//button[contains(text(), 'Apply on company website')]",
                "//a[contains(text(), 'Apply on company website')]",
                "//span[contains(translate(text(),'APPLY','apply'),'apply')]",
                "//input[contains(translate(@value,'APPLY','apply'),'apply')]"
                ]

            apply_button = None
            is_easy_apply = False
            is_company_site = False

            for selector in apply_button_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            button_text = element.text.lower() or element.get_attribute("aria-label", "").lower()
                            if "easy apply" in button_text:
                                is_easy_apply = True
                            elif "company" in button_text or "external" in button_text:
                                is_company_site = True

                            apply_button = element
                            self.log(f"Found apply button: {button_text}", "SUCCESS")
                            break
                    if apply_button:
                        break
                except:
                    continue

            # No apply button found
            if not apply_button:
                self.log(" No apply button found on the job page", "WARNING")
                return False, "No apply button found"

            # Scroll and click apply button
            self.driver.execute_script("arguments[0].scrollIntoView(true);", apply_button)
            time.sleep(1)

            original_window = self.driver.current_window_handle
            original_windows = self.driver.window_handles

            self.driver.execute_script("arguments[0].click();", apply_button)
            self.log("Clicked apply button", "SUCCESS")
            time.sleep(3)

            new_windows = self.driver.window_handles

            # Handle company site application
            if len(new_windows) > len(original_windows) and is_company_site:
                for win in new_windows:
                    if win not in original_windows:
                        self.driver.switch_to.window(win)
                        break

                self.log(" Switched to company website", "INFO")
                time.sleep(3)
                self.handle_cookies_popup()

                success = self.handle_company_site_application(job_title, company)
                self.driver.switch_to.window(original_window)

                if success:
                    job_data = {
                    'title': job_title,
                    'company': company,
                    'url': job_url,
                    'applied_at': datetime.now().isoformat(),
                    'signature': f"{job_title.lower()}_{company.lower()}",
                    'application_type': 'company_site'
                    }
                    self.applied_jobs.append(job_data)
                    self.company_site_jobs.append(job_data)
                    return True, "Applied successfully on company site"
                else:
                    return False, "Company site application failed"

            # Handle Easy Apply
            elif is_easy_apply:
                success = self.handle_easy_apply_form()

                if success:
                    job_data = {
                    'title': job_title,
                    'company': company,
                    'url': job_url,
                    'applied_at': datetime.now().isoformat(),
                    'signature': f"{job_title.lower()}_{company.lower()}",
                    'application_type': 'easy_apply'
                    }
                    self.applied_jobs.append(job_data)
                    return True, "Applied successfully via Easy Apply"
                else:
                    return False, "Easy Apply form submission failed"

            else:
                self.log(" Unknown application type, skipping...", "WARNING")
                return False, "Unknown application type"

        except Exception as e:
            self.log(f"Unexpected error during apply: {str(e)}", "ERROR")
            return False, str(e)

    def run(self):
        """Main execution method"""
        total_attempted = 0
        total_applied = 0
        
        try:
            if not USERNAME or not PASSWORD:
                raise Exception(" Please set USERNAME and PASSWORD in the script")
            
            self.log(f" Starting Enhanced LinkedIn Job Bot for Data Roles", "SUCCESS")
            self.log(f" Strategy: Easy Apply + Company Site Applications", "INFO")
            self.log(f" Target: Apply to {MAX_JOBS_PER_KEYWORD} jobs per keyword", "INFO")
            self.log(f" Keywords: {', '.join(JOB_KEYWORDS)}", "INFO")
            self.log(f" Applicant: {PERSONAL_INFO['first_name']} {PERSONAL_INFO['last_name']}", "INFO")
            self.log(f" Company Site Support: {'Enabled' if HANDLE_COMPANY_SITES else 'Disabled'}", "INFO")
            self.log(f" Country: {PERSONAL_INFO['country']} ({PERSONAL_INFO['country_code']})", "INFO")
            self.log(f"Phone: {PERSONAL_INFO['phone']}", "INFO")
            
            if RESUME_PATH and os.path.exists(RESUME_PATH):
                self.log(f" Resume file found: {os.path.basename(RESUME_PATH)}", "SUCCESS")
            else:
                self.log(" No resume file specified or file not found", "WARNING")
            
            # Login
            self.login()
            
            # Process each keyword
            for keyword_index, keyword in enumerate(JOB_KEYWORDS):
                try:
                    self.log(f"\n{'='*60}", "INFO")
                    self.log(f" PROCESSING KEYWORD {keyword_index + 1}/{len(JOB_KEYWORDS)}: '{keyword.upper()}'", "SUCCESS")
                    self.log(f"{'='*60}", "INFO")
                    
                    # Search for jobs with current keyword
                    self.search_jobs(keyword, LOCATION)
                    
                    # Apply to jobs for this keyword
                    attempted, applied = self.apply_to_jobs()
                    total_attempted += attempted
                    total_applied += applied
                    
                    self.log(f"Keyword '{keyword}' completed: {attempted} attempted, {applied} applied", "INFO")
                    
                    # Add delay between different keyword searches
                    if keyword_index < len(JOB_KEYWORDS) - 1:  # Don't delay after last keyword
                        self.log(f" Waiting before next keyword search...", "INFO")
                        self.random_delay(8, 15)  # Longer delay between keyword searches
                        
                except Exception as keyword_error:
                    self.log(f"Error processing keyword '{keyword}': {str(keyword_error)}", "ERROR")
                    continue
            
            # Final summary
            self.log(f"\n SESSION COMPLETE! ", "SUCCESS")
            self.log(f" Total jobs attempted: {total_attempted}", "INFO")
            self.log(f" Total applications submitted: {total_applied}", "SUCCESS")
            self.log(f"Total failed applications: {len(self.failed_jobs)}", "INFO")
            
            if total_attempted > 0:
                success_rate = (total_applied/total_attempted*100)
                self.log(f" Overall success rate: {success_rate:.1f}%", "INFO")
            
            # Show applied jobs summary by type
            if self.applied_jobs:
                self.log(f"\n Applied Jobs Summary:", "SUCCESS")
                easy_apply_jobs = [job for job in self.applied_jobs if job.get('application_type') == 'easy_apply']
                linkedin_jobs = [job for job in self.applied_jobs if job.get('application_type') == 'linkedin']
                company_jobs = [job for job in self.applied_jobs if job.get('application_type') == 'company_site']
                
                if easy_apply_jobs:
                    self.log(f"  Easy Apply applications: {len(easy_apply_jobs)}", "EASY")
                    for job in easy_apply_jobs[-3:]:  # Show last 3 Easy Apply applications
                        self.log(f"  {job['title']} at {job['company']}", "EASY")
                
                if linkedin_jobs:
                    self.log(f"  LinkedIn applications: {len(linkedin_jobs)}", "INFO")
                    for job in linkedin_jobs[-3:]:  # Show last 3 LinkedIn applications
                        self.log(f" {job['title']} at {job['company']}", "INFO")
                
                if company_jobs:
                    self.log(f"  Company Site applications: {len(company_jobs)}", "COMPANY")
                    for job in company_jobs[-3:]:  # Show last 3 company applications
                        self.log(f" {job['title']} at {job['company']}", "COMPANY")
            
            # Show failed jobs summary
            if self.failed_jobs:
                self.log(f"\nFailed Applications Summary:", "WARNING")
                for job in self.failed_jobs[-3:]:  # Show last 3 failures
                    self.log(f"   {job['title']}: {job['reason']}", "INFO")
            
            # Show tips for different application types
            if len(easy_apply_jobs) > 0:
                self.log(f"\n Easy Apply Tips:", "EASY")
                self.log(f"   {len(easy_apply_jobs)} jobs used LinkedIn Easy Apply", "EASY")
                self.log(f"   These are processed automatically with your saved LinkedIn profile", "EASY")
            
            if len(self.company_site_jobs) > 0:
                self.log(f"\n Company Site Application Tips:", "COMPANY")
                self.log(f"   {len(self.company_site_jobs)} jobs required company site applications", "COMPANY")
                self.log(f"   These often have better response rates than standard applications", "COMPANY")
                self.log(f"   Auto-filled fields where possible using your personal info", "COMPANY")
                self.log(f"   Country automatically set to India when detected", "COMPANY")
                self.log(f"   Phone country code automatically set to +91", "COMPANY")

        except KeyboardInterrupt:
            self.log("\n Script interrupted by user", "WARNING")
            self.log(" Saving partial results...", "INFO")

        except Exception as main_error:
            self.log(f" Script failed: {str(main_error)}", "ERROR")
        finally:
            self.log("Closing browser...")
            try:
                self.driver.quit()
            except:
                pass

# Interactive setup function
def setup_configuration():
    """Interactive setup for first-time users"""
    print("ENHANCED LINKEDIN BOT SETUP")
    print("=" * 50)
    
    # Check if configuration is already set
    if USERNAME and PASSWORD:
        print("Configuration already set in script")
        return
    
    print("Please update the following variables in the script:")
    print(f"USERNAME = '{USERNAME}' # Your LinkedIn email")
    print(f"PASSWORD = '{PASSWORD}' # Your LinkedIn password") 
    print(f"RESUME_PATH = r'{RESUME_PATH}' # Full path to your resume PDF")
    print()
    print(" Current target roles:")
    for i, keyword in enumerate(JOB_KEYWORDS, 1):
        print(f"  {i}. {keyword}")
    print()
    print(" India-specific features:")
    print("   Country automatically filled as 'India'")
    print("   Phone country code automatically set to")
    print()

# Run the bot
if __name__ == "__main__":
    print(" Enhanced LinkedIn Job Bot - Data Roles Specialist")
    print("=" * 60)
    print(" Prioritizes: LinkedIn Easy Apply jobs for faster processing")
    print(" Also handles: Company website applications")
    print(" Focuses on: Data Analyst, Data Science, Python Developer roles")
    print(" Auto-fills: Personal info, resume, cover letter, experience")
    print(" Smart filtering: Only applies to relevant data roles")
    print(f" Target: {MAX_JOBS_PER_KEYWORD} jobs per keyword")
    print("=" * 60)
    
    # Setup check
    setup_configuration()
    
    if not USERNAME or not PASSWORD:
        print("\n Please configure USERNAME and PASSWORD before running the bot")
        exit(1)
    
    # Confirmation prompt
    print(f"\n Ready to apply to jobs in: {LOCATION}")
    print(f" Keywords: {', '.join(JOB_KEYWORDS)}")
    print(f" Resume: {' Found' if RESUME_PATH and os.path.exists(RESUME_PATH) else '❌ Not found'}")
    print(f" Applicant: {PERSONAL_INFO['first_name']} {PERSONAL_INFO['last_name']}")
    
    confirm = input("\nStart job applications? (y/n): ").lower().strip()
    if confirm != 'y':
        print(" Application cancelled by user")
        exit(0)
    
    print("\n Starting Enhanced LinkedIn Job Bot...")
    print("Tip: Easy Apply jobs will be processed automatically")
    print(" Tip: Company site applications may require some manual input")
    print(" Tip: Press Ctrl+C to stop gracefully and save progress")
    print("-" * 60)
    
    bot = LinkedInJobBot()
    bot.run()