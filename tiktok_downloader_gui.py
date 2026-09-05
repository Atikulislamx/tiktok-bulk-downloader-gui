import concurrent.futures
import os
import random
import re
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import pypdf
import requests


class TikTokDownloaderApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Ultimate TikTok Bulk Downloader with Failed Log")
    self.root.geometry("800x720")
    self.root.config(bg="#f0f0f0")

    self.is_running = False
    self.success_count = 0
    self.failed_count = 0
    self.failed_log_filename = "failed_downloads.txt"

    # Title Label
    title_label = tk.Label(
        root,
        text="TikTok Bulk Downloader & Failed URL Logger",
        font=("Arial", 14, "bold"),
        bg="#f0f0f0",
        fg="#333",
    )
    title_label.pack(pady=10)

    # Frame for controls
    control_frame = tk.Frame(root, bg="#f0f0f0")
    control_frame.pack(pady=5, fill=tk.X, padx=20)

    # PDF File Selection
    tk.Label(
        control_frame,
        text="PDF File:",
        font=("Arial", 10),
        bg="#f0f0f0",
    ).grid(row=0, column=0, sticky="w", pady=5)
    self.pdf_path_var = tk.StringVar()
    self.pdf_entry = tk.Entry(
        control_frame, textvariable=self.pdf_path_var, width=58
    )
    self.pdf_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(control_frame, text="Browse...", command=self.browse_pdf).grid(
        row=0, column=2, pady=5
    )

    # Output Folder Selection
    tk.Label(
        control_frame,
        text="Output Folder:",
        font=("Arial", 10),
        bg="#f0f0f0",
    ).grid(row=1, column=0, sticky="w", pady=5)
    self.output_path_var = tk.StringVar(value="./tiktok_downloads")
    self.output_entry = tk.Entry(
        control_frame, textvariable=self.output_path_var, width=58
    )
    self.output_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(control_frame, text="Browse...", command=self.browse_output).grid(
        row=1, column=2, pady=5
    )

    # Proxy File Selection (Optional)
    tk.Label(
        control_frame,
        text="Proxy List (Opt):",
        font=("Arial", 10),
        bg="#f0f0f0",
    ).grid(row=2, column=0, sticky="w", pady=5)
    self.proxy_path_var = tk.StringVar()
    self.proxy_entry = tk.Entry(
        control_frame, textvariable=self.proxy_path_var, width=58
    )
    self.proxy_entry.grid(row=2, column=1, padx=5, pady=5)
    tk.Button(control_frame, text="Browse...", command=self.browse_proxy).grid(
        row=2, column=2, pady=5
    )

    # Action Buttons Frame
    btn_frame = tk.Frame(root, bg="#f0f0f0")
    btn_frame.pack(pady=10)

    self.start_btn = tk.Button(
        btn_frame,
        text="Start Downloading",
        font=("Arial", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        padx=15,
        pady=5,
        command=self.start_download_thread,
    )
    self.start_btn.pack(side=tk.LEFT, padx=10)

    self.stop_btn = tk.Button(
        btn_frame,
        text="Stop",
        font=("Arial", 11, "bold"),
        bg="#f44336",
        fg="white",
        padx=15,
        pady=5,
        state=tk.DISABLED,
        command=self.stop_download,
    )
    self.stop_btn.pack(side=tk.LEFT, padx=10)

    # Statistics Dashboard Frame
    stats_frame = tk.Frame(root, bg="#e0e0e0", bd=1, relief=tk.SOLID)
    stats_frame.pack(fill=tk.X, padx=20, pady=5)

    self.stats_label = tk.Label(
        stats_frame,
        text="Statistics -> Downloaded: 0 | Failed: 0 | Remaining: 0",
        font=("Arial", 10, "bold"),
        bg="#e0e0e0",
        fg="#333",
    )
    self.stats_label.pack(pady=5)

    # Progress Bar Section
    progress_frame = tk.Frame(root, bg="#f0f0f0")
    progress_frame.pack(fill=tk.X, padx=20, pady=5)

    self.progress_label = tk.Label(
        progress_frame,
        text="Progress: 0 / 0 videos (0%)",
        font=("Arial", 10, "bold"),
        bg="#f0f0f0",
    )
    self.progress_label.pack(anchor="w", pady=2)

    self.progress_bar = ttk.Progressbar(
        progress_frame, orient="horizontal", length=740, mode="determinate"
    )
    self.progress_bar.pack(fill=tk.X, pady=2)

    # Console Output Log Area
    tk.Label(
        root,
        text="Download Progress & Logs:",
        font=("Arial", 10, "bold"),
        bg="#f0f0f0",
    ).pack(anchor="w", padx=20)
    self.log_area = scrolledtext.ScrolledText(
        root, width=90, height=12, font=("Consolas", 9)
    )
    self.log_area.pack(pady=5, padx=20)

  def browse_pdf(self):
    filename = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    if filename:
      self.pdf_path_var.set(filename)

  def browse_output(self):
    dirname = filedialog.askdirectory()
    if dirname:
      self.output_path_var.set(dirname)

  def browse_proxy(self):
    filename = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if filename:
      self.proxy_path_var.set(filename)

  def log(self, message):
    self.log_area.insert(tk.END, message + "\n")
    self.log_area.see(tk.END)

  def update_stats_and_progress(self, current, total):
    percent = int((current / total) * 100) if total > 0 else 0
    self.progress_bar["value"] = percent
    self.progress_label.config(
        text=f"Progress: {current} / {total} videos ({percent}%)"
    )
    remaining = max(0, total - (self.success_count + self.failed_count))
    self.stats_label.config(
        text=(
            f"Statistics -> Downloaded: {self.success_count} | Failed:"
            f" {self.failed_count} | Remaining/Queued: {remaining}"
        )
    )

  def log_failed_url_to_file(self, url):
    """Appends a permanently failed URL to failed_downloads.txt instantly."""
    try:
      with open(self.failed_log_filename, "a", encoding="utf-8") as f:
        f.write(url + "\n")
    except Exception:
      pass

  def start_download_thread(self):
    pdf_file = self.pdf_path_var.get()
    if not pdf_file or not os.path.exists(pdf_file):
      messagebox.showerror(
          "Error", "Please select a valid PDF file containing TikTok URLs!"
      )
      return

    self.is_running = True
    self.success_count = 0
    self.failed_count = 0
    self.start_btn.config(state=tk.DISABLED)
    self.stop_btn.config(state=tk.NORMAL)

    # Initialize or clear/prepare failed_downloads.txt for the new session
    try:
      with open(self.failed_log_filename, "w", encoding="utf-8") as f:
        f.write("# Failed TikTok Video URLs Log\n")
    except Exception:
      pass

    threading.Thread(target=self.run_downloader, daemon=True).start()

  def stop_download(self):
    self.is_running = False
    self.log("[INFO] Stop requested by user. Finishing current tasks...")
    self.start_btn.config(state=tk.NORMAL)
    self.stop_btn.config(state=tk.DISABLED)

  def test_proxy(self, proxy):
    proxies_dict = {"http": proxy, "https": proxy}
    try:
      response = requests.get(
          "https://www.tiktok.com", proxies=proxies_dict, timeout=4
      )
      if response.status_code == 200:
        return True
    except Exception:
      pass
    return False

  def run_downloader(self):
    pdf_file = self.pdf_path_var.get()
    base_output_dir = self.output_path_var.get()
    proxy_file = self.proxy_path_var.get()

    os.makedirs(base_output_dir, exist_ok=True)

    self.log(f"Reading URLs from PDF: {pdf_file}...")
    try:
      reader = pypdf.PdfReader(pdf_file)
      urls = []
      for page in reader.pages:
        text = page.extract_text()
        found = re.findall(r"https://www\.tiktok\.com/[^\s]+", text)
        urls.extend(found)
      urls = list(dict.fromkeys(urls))
      self.log(f"Successfully extracted {len(urls)} unique TikTok video URLs.")
    except Exception as e:
      self.log(f"[ERROR] Failed to read PDF: {e}")
      self.start_btn.config(state=tk.NORMAL)
      self.stop_btn.config(state=tk.DISABLED)
      return

    # Proxy Health Checker
    live_proxies = []
    if proxy_file and os.path.exists(proxy_file):
      self.log("Loading and testing proxy health...")
      with open(proxy_file, "r", encoding="utf-8") as f:
        raw_proxies = [line.strip() for line in f if line.strip()]

      with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {
            executor.submit(self.test_proxy, p): p for p in raw_proxies
        }
        for future in concurrent.futures.as_completed(future_to_proxy):
          p = future_to_proxy[future]
          try:
            if future.result():
              live_proxies.append(p)
          except Exception:
            pass

      if live_proxies:
        self.log(
            f"Proxy health check passed! {len(live_proxies)}/{len(raw_proxies)}"
            " proxies are alive."
        )
      else:
        self.log(
            "[WARNING] All proxies failed. Falling back to direct connection."
        )
    else:
      self.log("No proxy file selected. Proceeding with direct connection...")

    # Cookies check
    cookie_arg = []
    if os.path.exists("cookies.txt"):
      self.log("Found Netscape cookies.txt file. Using it for authentication.")
      cookie_arg = ["--cookies", "cookies.txt"]
    else:
      self.log("Warning: No cookies.txt found. Running without cookies...")

    remaining_urls = urls
    total_urls_count = len(urls)
    pass_num = 1
    max_passes = 3

    def download_single_video(url):
      if not self.is_running:
        return False

      creator_match = re.search(r"tiktok\.com/(@[\w\.]+)", url)
      creator_folder = (
          os.path.join(base_output_dir, creator_match.group(1))
          if creator_match
          else base_output_dir
      )
      os.makedirs(creator_folder, exist_ok=True)

      command = (
          [
              "yt-dlp",
              "-P",
              creator_folder,
              "--download-archive",
              "downloads_archive.txt",
          ]
          + cookie_arg
          + [
              "--geo-bypass",
              "--user-agent",
              (
                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
              ),
          ]
      )

      if live_proxies:
        command.extend(["--proxy", random.choice(live_proxies)])

      command.append(url)

      for attempt in range(1, 4):
        if not self.is_running:
          return False
        try:
          subprocess.run(
              command,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE,
              text=True,
              check=True,
          )
          return True
        except subprocess.CalledProcessError:
          time.sleep(random.uniform(2, 5))
      return False

    global_processed = 0
    while remaining_urls and pass_num <= max_passes and self.is_running:
      self.log(
          f"\n--- DOWNLOAD PASS #{pass_num}: {len(remaining_urls)} videos"
          " remaining ---"
      )
      next_round_failed = []

      with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {
            executor.submit(download_single_video, url): url
            for url in remaining_urls
        }

        for future in concurrent.futures.as_completed(future_to_url):
          if not self.is_running:
            break
          url = future_to_url[future]
          global_processed += 1
          try:
            success = future.result()
            if success:
              self.success_count += 1
              self.log(f"[SUCCESS] {url}")
            else:
              self.failed_count += 1
              self.log(f"[FAILED] {url}")
              next_round_failed.append(url)
              self.log_failed_url_to_file(url)
          except Exception:
            self.failed_count += 1
            self.log(f"[ERROR] {url}")
            next_round_failed.append(url)
            self.log_failed_url_to_file(url)

          self.root.after(
              0,
              lambda c=global_processed, t=total_urls_count: (
                  self.update_stats_and_progress(c, t)
              ),
          )
          time.sleep(random.uniform(1, 2))

      remaining_urls = next_round_failed
      if remaining_urls and pass_num < max_passes and self.is_running:
        self.log(
            f"Pass #{pass_num} finished. {len(remaining_urls)} failed. Waiting"
            " 30s before next pass..."
        )
        time.sleep(30)
        pass_num += 1
      else:
        break

    if not self.is_running:
      self.log("\n[INFO] Download process stopped by user.")
      messagebox.showinfo(
          "Stopped",
          f"Download stopped.\nSuccessfully Downloaded: {self.success_count}\nFailed"
          f" Items: {self.failed_count}\nSaved to: {self.failed_log_filename}",
      )
    elif remaining_urls:
      self.log(
          f"\n[WARNING] {len(remaining_urls)} URLs permanently failed. Saved to"
          f" '{self.failed_log_filename}'"
      )
      messagebox.showwarning(
          "Completed with Errors",
          f"Process finished with some permanent failures.\nDownloaded:"
          f" {self.success_count}\nFailed Logged to"
          f" '{self.failed_log_filename}': {len(remaining_urls)}",
      )
    else:
      self.log("\n==========================================")
      self.log("ALL VIDEOS DOWNLOADED SUCCESSFULLY!")
      self.log("==========================================")
      self.update_stats_and_progress(total_urls_count, total_urls_count)
      messagebox.showinfo(
          "Success!",
          "All videos downloaded successfully without watermarks!\nTotal"
          f" Downloaded: {self.success_count}",
      )

    self.start_btn.config(state=tk.NORMAL)
    self.stop_btn.config(state=tk.DISABLED)


if __name__ == "__main__":
  root = tk.Tk()
  app = TikTokDownloaderApp(root)
  root.mainloop()
