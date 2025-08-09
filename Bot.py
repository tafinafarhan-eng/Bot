import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time
import logging

# Telegram Bot API Token
API_TOKEN = 'YOUR_API_TOKEN'
CHAT_ID = '@your_group_name_or_chat_id'

bot = Bot(token=API_TOKEN)

# Login URL
login_url = 'https://mediateluk.com/sms/index.php?login'
login_data = {
    'user': 'your_username',  # আপনার ইউজারনেম
    'password': 'your_password'  # আপনার পাসওয়ার্ড
}

# Start a session to maintain the login state
session = requests.Session()

# Logging setup to show errors or status
logging.basicConfig(level=logging.INFO)

# Perform login
def login():
    try:
        login_response = session.post(login_url, data=login_data)
        if login_response.status_code == 200:
            logging.info('Login Successful')
        else:
            logging.error(f'Login Failed with status code {login_response.status_code}')
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")

# "Today summaries" পেজ লোড করা
def get_summary_page():
    try:
        summary_url = 'https://mediateluk.com/sms/index.php?opt=shw_sum'
        summary_page = session.get(summary_url)
        summary_page.raise_for_status()  # To raise error for any HTTP issues
        return BeautifulSoup(summary_page.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while fetching summary page: {str(e)}")
        return None

# OTP খুঁজে পাওয়া গেলে টেলিগ্রামে পাঠানো
def send_otp_to_telegram(otp_data, country_name, service_name):
    formatted_message = f"""
🇸🇦 {country_name}
{service_name} 𝗢𝘁𝗽 𝘾𝙤𝙙𝙚 𝙍𝙚𝙘𝙚𝙞𝙫𝙚𝙙🎉

🔑 𝒀𝒐𝒖𝒓 𝑶𝑻𝑷 𝑪𝒐𝒅𝒆: {otp_data}

☎️ 𝑵𝒖𝒎𝒃𝒆𝒓: 9665546****062
⚙️ 𝑺𝒆𝒓𝒗𝒊𝒄𝒆: {service_name}
🌍 𝑪𝒐𝒖𝒏𝒕𝒓𝒚: {country_name} 🇸🇦
📩 𝐅𝐮𝐥𝐥 𝗠𝗮𝘀𝘀𝗮𝗴𝗲:
nullYour WhatsApp code {otp_data}

Don't share this code with others
"""
    try:
        bot.send_message(chat_id=CHAT_ID, text=formatted_message)
        logging.info(f"Sent OTP: {otp_data} from {country_name} ({service_name})")
    except Exception as e:
        logging.error(f"Error sending OTP to Telegram: {str(e)}")

# সেশন স্টার্ট করা
login()

# ২৪ ঘণ্টা বট চলবে এবং OTP চেক করবে
def keep_checking_for_otp():
    last_sent_otp = None

    # দেশ এবং সেবা নাম আলাদা আলাদা রাখা
    country_names = [
        "Saudi Arabia", "United States", "United Kingdom", "India", "UAE", 
        "Brazil", "Russia", "Australia", "Canada", "South Africa"
    ]

    service_names = [
        "WhatsApp", "Viber", "Signal", "Telegram", "Messenger", "Skype"
    ]

    while True:
        soup = get_summary_page()
        if soup is None:  # If we fail to fetch the page, skip this loop and retry
            logging.error("Skipping this cycle due to failure in fetching the page.")
            time.sleep(60)  # Wait before retrying
            continue
        
        # SMS ডেটা সংগ্রহ করা
        senders_data = soup.find_all('div', class_='sms-data')  # এখানে class_name আপনার পেজ অনুযায়ী হবে

        for sender in senders_data:
            sender_info = sender.get_text().strip()
            
            # OTP চেক করা
            if 'OTP' in sender_info:  
                # OTP ডুপ্লিকেট না হলে পাঠানো হবে
                if sender_info != last_sent_otp:
                    # সমস্ত দেশের জন্য প্রতিটি সেবার OTP পাঠানো
                    for country_name in country_names:
                        for service_name in service_names:
                            send_otp_to_telegram(sender_info, country_name, service_name)  # OTP পাঠানো
                            logging.info(f"Sending OTP from {country_name} using {service_name}")
                    last_sent_otp = sender_info  # OTP আপডেট করা
                else:
                    logging.info("Duplicate OTP, skipping.")
        
        time.sleep(60)  # প্রতি ১ মিনিট পর পর চেক করবে

# ২৪ ঘণ্টা চলমান রাখতে
keep_checking_for_otp()
