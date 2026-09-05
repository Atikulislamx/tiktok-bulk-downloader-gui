# 🚀 Ultimate TikTok Bulk Downloader (GUI & Automation Tool)

An advanced, open-source desktop application built with Python and Tkinter designed to bulk-download clean, unwatermarked TikTok videos directly from PDF link collections. 

Equipped with an intuitive graphical user interface, multi-threading, intelligent proxy health-checking, multi-pass error handling, and smart output organization.

---

## ✨ Key Features

* **🖥️ Graphical User Interface (GUI):** Clean desktop window featuring a file picker, live progress bars, a real-time statistics dashboard (`Downloaded | Failed | Remaining`), and status console logs.
* **⚡ Multi-Threaded Parallel Downloads:** Utilizes a thread pool executor to process multiple video downloads concurrently for maximum speed.
* **📂 Smart Creator Organization:** Automatically groups downloaded videos into dedicated subfolders based on the creator's username (e.g., `./tiktok_downloads/@username/`).
* **🔄 Smart Resume Support (`downloads_archive.txt`):** Remembers completed tasks across sessions. If stopped and restarted later, it instantly skips already-downloaded videos to prevent duplicates.
* **🛡️ Relentless Multi-Pass Error Handling:** Automatically retries failed or rate-limited links across multiple deep passes with human-like randomized delays.
* **🌐 Optional Proxy Rotation & Health Checker:** Automatically pings and filters out dead proxies from your custom proxy list on startup, falling back gracefully to direct connection mode if no proxy file is provided.
* **📝 Live Failed URL Logger (`failed_downloads.txt`):** Instantly records any permanently failed or broken links into a text file for quick review.
* **🍪 Authentication Support (`cookies.txt`):** Integrates seamlessly with Netscape-formatted cookie files to authenticate sessions and bypass TikTok's strict bot-detection walls and 403 errors.

---

## 🛠️ Prerequisites & Installation

Make sure you have **Python 3.10+** installed on your machine.

1. **Clone or Download this repository:**
   ```bash
   git clone https://github.com/Atikulislamx/tiktok-bulk-downloader-gui.git
   cd tiktok-bulk-downloader-gui

2. **Install Required Python Dependencies:**
   ```bash
   pip install -r requirements.txt

## ⚙️ Configuration & Setup

Before launching the tool, place the following optional/required files in the root project folder:

1. **Cookies File (`cookies.txt` - Strongly Recommended):**
* To bypass TikTok's strict bot-blocking and 403 errors, export your TikTok account cookies using a browser extension (such as *Get cookies.txt LOCALLY*) in **Netscape format**.
* Save the file strictly as `cookies.txt` inside the project folder.


2. **Proxy List File (`proxies.txt` - Optional):**
* If you wish to use proxy rotation to protect your IP during mass downloads, create a text file named `proxies.txt`.
* Add your proxies line by line (format: `http://ip:port` or `http://username:password@ip:port`). If left empty or if all proxies fail health checks, the tool will automatically fall back to direct connection mode without interruption.


## 🚀 How to Use

1. Run the graphical application script from your terminal:
```bash
python tiktok_downloader_gui.py

```


2. **Select your PDF file** containing the TikTok video URLs via the GUI file browser.
3. **Choose your output directory** where your unwatermarked videos will be organized into creator subfolders.
4. *(Optional)* Select your `proxies.txt` file using the proxy browser button.
5. Click **Start Downloading** and monitor the live statistics dashboard, progress bar, and console logs!

---

## 📂 Project Structure

* `tiktok_downloader_gui.py` — Main graphical application script.
* `requirements.txt` — Python package dependencies.
* `downloads_archive.txt` — Internal log tracking completed video IDs for safe resume support.
* `failed_downloads.txt` — Live log recording URLs that failed after all retry passes.

---

## 🤝 Contributing & Improving the Project

This project is completely open-source, and contributions are **hugely welcome**! Whether you want to fix bugs, optimize performance, or add new features:

1. Fork the Project (`https://github.com/Atikulislamx/tiktok-bulk-downloader-gui/fork`)
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
