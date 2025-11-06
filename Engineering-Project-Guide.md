# 🎓 Engineering Final Project: Network Intrusion Detection System
## Complete Step-by-Step Guide for Beginners

### 📋 What You're Building

You're creating a **smart security system** that watches your computer network and automatically detects when hackers try to attack it. Think of it like a security camera for your internet connection - it watches all the data flowing in and out, and alerts you when something suspicious happens.

---

## 🚀 PART 1: SETTING UP YOUR COMPUTER

### Step 1: Check Your Operating System

**If you have Windows:**
```
Press Windows Key + R
Type: cmd
Press Enter
In the black window, type: python --version
```

**If you have Linux/Ubuntu:**
```
Press Ctrl + Alt + T (opens terminal)
Type: python3 --version
```

**If you have macOS:**
```
Press Cmd + Space, type "Terminal", press Enter
Type: python3 --version
```

✅ **Expected Result:** You should see something like `Python 3.8.10` or higher
❌ **If you see an error:** Download Python from https://python.org/downloads/

### Step 2: Create Your Project Folder

**On Windows:**
```
1. Right-click on Desktop
2. Click "New" → "Folder"
3. Name it: "MyIDS_Project"
4. Double-click to open it
```

**On Linux/macOS:**
```
1. Open Terminal
2. Type: mkdir ~/Desktop/MyIDS_Project
3. Type: cd ~/Desktop/MyIDS_Project
```

### Step 3: Download the Project Files

**Method 1 - Easy Way (Copy-Paste):**
1. Go back to our conversation
2. Find the message with `network_ids.py` file
3. Click the download button and save it to your `MyIDS_Project` folder
4. Do the same for `requirements.txt`
5. Do the same for `IDS-Setup-Guide.md`

**Method 2 - Manual Creation:**
1. Open Notepad (Windows) or TextEdit (Mac) or gedit (Linux)
2. Copy the entire code from `network_ids.py` in our conversation
3. Paste it and save as `network_ids.py` in your project folder
4. Repeat for `requirements.txt`

---

## 🔧 PART 2: INSTALLING REQUIRED SOFTWARE

### Step 4: Install Python Libraries

**Open Command Prompt/Terminal in your project folder:**

**Windows:**
```
1. Hold Shift + Right-click in your MyIDS_Project folder
2. Click "Open PowerShell window here" or "Open command window here"
3. Type: pip install scapy scikit-learn numpy python-dateutil
4. Press Enter and wait (this might take 2-3 minutes)
```

**Linux/macOS:**
```
1. Open Terminal
2. Type: cd ~/Desktop/MyIDS_Project
3. Type: pip3 install scapy scikit-learn numpy python-dateutil
4. Press Enter and wait
```

✅ **Expected Result:** You'll see lots of text downloading and installing packages
❌ **If you see permission errors on Linux/macOS:** Try `sudo pip3 install...`

### Step 5: Verify Installation

Type this command:
```python
python -c "import scapy; import sklearn; print('SUCCESS: All libraries installed!')"
```

✅ **Expected Result:** `SUCCESS: All libraries installed!`
❌ **If you see errors:** Repeat Step 4

---

## 🧪 PART 3: TESTING YOUR IDS (NO TECHNICAL KNOWLEDGE NEEDED)

### Step 6: Run Your First Test

This test runs fake attack scenarios to make sure everything works:

**In your command prompt/terminal (in the project folder):**
```
python network_ids.py test
```

### Step 7: Understanding Test Results

You should see something like this:
```
[TEST MODE] Starting IDS Test...

[Packet 1] IP / TCP 192.168.1.10:1234 > 192.168.1.1:http A
  ✓ No threats detected

[Packet 7] IP / TCP 10.0.0.3:5680 > 192.168.1.100:http S
  ⚠️  THREATS DETECTED: 1
    - SYN Flood Attack (signature) - Confidence: 1.00

[Packet 9] IP / TCP 192.168.1.200:4321 > 192.168.1.100:smtp S
  ⚠️  THREATS DETECTED: 1
    - Port Scanning (signature) - Confidence: 1.00
```

**What this means:**
- ✅ Green checkmarks = Normal, safe internet traffic
- ⚠️ Warning signs = Detected cyber attacks!
- **SYN Flood Attack** = Someone trying to crash a website
- **Port Scanning** = Someone looking for ways to break into computers

🎉 **If you see this output, your IDS is working perfectly!**

---

## 🔴 PART 4: LIVE TESTING ON REAL NETWORK

### Step 8: Find Your Network Interface

**Windows:**
```
1. Press Windows Key + R
2. Type: cmd
3. In command prompt, type: ipconfig
4. Look for your network adapter name (usually "Ethernet" or "Wi-Fi")
```

**Linux:**
```
1. Open Terminal
2. Type: ip link show
3. Look for names like: eth0, wlan0, enp3s0
4. Write down the name (you'll need it later)
```

**macOS:**
```
1. Open Terminal
2. Type: ifconfig
3. Look for en0, en1, etc.
4. Write down the active one
```

### Step 9: Modify Code for Your Network

1. Open `network_ids.py` in any text editor
2. Scroll to the very bottom of the file
3. Find these lines (around line 500):
```python
        # Uncomment to start IDS (requires root privileges)
        # ids = IntrusionDetectionSystem(interface="eth0")  # Change interface
        # ids.start()
```

4. Change them to:
```python
        # Uncomment to start IDS (requires root privileges)
        ids = IntrusionDetectionSystem(interface="YOUR_INTERFACE_NAME")  # Change interface
        ids.start()
```

Replace `YOUR_INTERFACE_NAME` with what you found in Step 8 (like "eth0", "wlan0", etc.)

### Step 10: Run Live Monitoring

**IMPORTANT:** This requires administrator privileges!

**Windows (Run as Administrator):**
```
1. Right-click on Command Prompt
2. Choose "Run as Administrator"
3. Navigate to your project: cd Desktop\MyIDS_Project
4. Type: python network_ids.py
```

**Linux/macOS:**
```
sudo python3 network_ids.py
```

### Step 11: What You'll See During Live Monitoring

```
======================================================================
  NETWORK INTRUSION DETECTION SYSTEM (IDS)
  AI-Powered Security Monitoring
======================================================================
[+] Starting IDS on interface: wlan0
[+] Press Ctrl+C to stop

[STATS] Packets: 100 | Threats: 0
[STATS] Packets: 200 | Threats: 1
```

This means:
- Your IDS is watching network traffic
- It analyzed 200 packets of data
- It found 1 potential threat

---

## 🔬 PART 5: CREATING ATTACKS FOR TESTING (SAFE & LEGAL)

### Step 12: Generate Test Traffic

**Method 1 - Simple Web Traffic:**
```
1. Open your web browser
2. Visit different websites: google.com, youtube.com, github.com
3. Your IDS should show normal traffic (no threats)
```

**Method 2 - Create Suspicious Traffic (Advanced):**

If you have another computer on the same network:

1. **Install nmap** (network scanner):
   - Windows: Download from https://nmap.org/download.html
   - Linux: `sudo apt install nmap`
   - macOS: `brew install nmap`

2. **Run a port scan** (this will trigger your IDS):
```
nmap -sS 192.168.1.1-10
```

3. **Watch your IDS detect the scan!**

### Step 13: Understanding Alert Output

When your IDS detects an attack, you'll see:
```json
{
  "alert_id": 1,
  "timestamp": "2025-10-22T01:50:00.123456",
  "threat_type": "signature",
  "threat_name": "Port Scanning",
  "source_ip": "192.168.1.100",
  "destination_ip": "192.168.1.1",
  "confidence": 1.0,
  "severity": "HIGH"
}
```

**Translation:**
- **alert_id**: This is the 1st alert
- **timestamp**: When it happened
- **threat_name**: What type of attack
- **source_ip**: Who did it (attacker's computer)
- **destination_ip**: Target computer
- **confidence**: How sure the system is (1.0 = 100% sure)
- **severity**: How dangerous it is

---

## 📊 PART 6: COLLECTING DATA FOR YOUR PROJECT

### Step 14: Save Your Results

1. Your IDS automatically creates a log file: `ids_alerts.log`
2. Take screenshots of:
   - Test mode results
   - Live monitoring console output
   - Any alerts generated
   - The log file contents

### Step 15: Analyze Your Data

Create a simple table:

| Test Type | Packets Analyzed | Threats Detected | Attack Types Found |
|-----------|------------------|------------------|--------------------|
| Test Mode | 11 | 3 | SYN Flood, Port Scan, Abnormal Traffic |
| Normal Web | 500 | 0 | None |
| Port Scan | 150 | 5 | Port Scanning |

---

## 📝 PART 7: DOCUMENTATION FOR YOUR PROJECT REPORT

### Step 16: What to Include in Your Report

**1. Introduction:**
"I built an Intrusion Detection System using Python and machine learning to automatically detect cyber attacks on computer networks."

**2. Technical Details:**
- Programming Language: Python
- Key Libraries: Scapy (packet capture), Scikit-learn (machine learning)
- Detection Methods: Signature-based + Anomaly-based
- Detected Attacks: SYN Flood, Port Scanning, DDoS, Abnormal Traffic

**3. Results:**
- Include your screenshots
- Show the data table from Step 15
- Explain what each attack means

**4. Testing Process:**
- Describe the test mode (simulated attacks)
- Explain live testing on your network
- Show how you generated safe test attacks

### Step 17: Create a Demo Video

Record your screen while:
1. Running test mode
2. Explaining the output
3. Running live monitoring
4. Triggering a port scan
5. Showing the alert generated

---

## 🚨 TROUBLESHOOTING COMMON PROBLEMS

### Problem 1: "Permission denied" error
**Solution:**
- Windows: Run Command Prompt as Administrator
- Linux/macOS: Use `sudo python3 network_ids.py`

### Problem 2: "No module named 'scapy'"
**Solution:**
```
pip install scapy
```
Or on Linux/macOS: `pip3 install scapy`

### Problem 3: No packets captured
**Solution:**
1. Make sure you're connected to internet
2. Try browsing websites while IDS is running
3. Check your interface name is correct

### Problem 4: Interface not found
**Solution:**
1. Run `ipconfig` (Windows) or `ip link show` (Linux)
2. Update the interface name in your code
3. Make sure the interface is "UP" and connected

---

## 🎯 PART 8: MAKING YOUR PROJECT IMPRESSIVE

### Step 18: Add These Features (Optional but Cool)

**1. Create a simple dashboard:**
```python
# Add this to your code to count different attack types
attack_counts = {
    'syn_flood': 0,
    'port_scan': 0,
    'ddos': 0,
    'anomaly': 0
}
```

**2. Generate a report:**
```python
# At the end, print statistics
print(f"Total Attacks Detected: {sum(attack_counts.values())}")
print(f"Most Common Attack: {max(attack_counts, key=attack_counts.get)}")
```

### Step 19: Advanced Testing (If You Want Extra Credit)

**Download attack datasets:**
1. Go to https://www.unb.ca/cic/datasets/ids-2017.html
2. Download sample network traffic data
3. Modify your IDS to read from files instead of live network
4. Test against thousands of real attack examples

---

## 🏆 PART 9: PROJECT PRESENTATION TIPS

### Step 20: Prepare Your Presentation

**Slide 1: Problem Statement**
"Cyber attacks are increasing. We need automated systems to detect them quickly."

**Slide 2: Solution**
"I built an AI-powered Intrusion Detection System that monitors network traffic and automatically identifies attacks."

**Slide 3: Technology Used**
- Python programming
- Scapy for network packet analysis
- Machine learning for anomaly detection
- Real-time monitoring and alerting

**Slide 4: Demo**
Show your live demo or recorded video

**Slide 5: Results**
Show your detection statistics and examples

**Slide 6: Future Improvements**
- Web dashboard interface
- Email notifications
- Integration with enterprise security tools

---

## ✅ FINAL CHECKLIST

Before submitting your project, make sure you have:

- [ ] Working IDS code (`network_ids.py`)
- [ ] Requirements file (`requirements.txt`)
- [ ] Documentation (`IDS-Setup-Guide.md`)
- [ ] Screenshots of test mode results
- [ ] Screenshots of live monitoring
- [ ] Log file with detected attacks (`ids_alerts.log`)
- [ ] Data analysis table
- [ ] Project report (5-10 pages)
- [ ] Demo video (3-5 minutes)
- [ ] Presentation slides (6-8 slides)

---

## 🎉 CONGRATULATIONS!

You've just built a professional-grade Intrusion Detection System! This project demonstrates:

✅ **Programming Skills:** Python, file handling, data processing
✅ **Networking Knowledge:** Packet analysis, protocols, network security
✅ **Machine Learning:** Anomaly detection, pattern recognition
✅ **Cybersecurity:** Attack detection, threat analysis
✅ **Project Management:** Documentation, testing, presentation

**This is a college/university-level project that shows real technical competence!**

---

## 📞 Need Help?

If you get stuck:

1. **Check the error message** - it usually tells you what's wrong
2. **Try the troubleshooting section** above
3. **Google the error message** - Stack Overflow has solutions
4. **Start with test mode** - it's safer and easier
5. **Make sure Python and libraries are installed correctly**

**Remember:** Every software engineer faces bugs and errors. The skill is in debugging and finding solutions!

Good luck with your final project! 🚀