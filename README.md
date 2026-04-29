<h1 align="center"> 🛡️ PCAP Storyteller </h1>

<p align="center">
  <strong>The Forensic detective for Students & Educators</strong>
</p>

<p align="center">
  Transform messy PCAP network traffic into an interactive, visual storyboard. Built from the ground up to make network forensics easy to teach, learn, and understand.
</p>

---

## 🌟 Why PCAP StoryTeller? (The Problem)

Traditional tools like **Wireshark** are built for experts but often overwhelm students with "Data Overload." 

- **The Wireshark Problem**: 50,000 packets look like a confusing spreadsheet. It's hard to see the "Story."
- **Our Solution**: We automatically **Link** related events (DNS ➔ HTTP ➔ TLS) and use **Heuristic Intelligence** to flag hacker behavior so you can focus on the investigation, not the noise.

---

## 🎓 Educational Curriculum

We have organized a complete 9-module learning path in the `documentation/` folder:

1.  [**00 | Intro & Problem Statement**](documentation/00_Introduction_and_Problem_Statement.md) - Why forensics is hard and how we fix it.
2.  [**01 | Definitions & Terminology**](documentation/01_Definitions_and_Terminology.md) - DNS as a phonebook, Packets as envelopes.
3.  [**02 | Tech Stack & Libraries**](documentation/02_Tech_Stack_and_Flask_Libraries.md) - Why we use Flask, Scapy, and Folium.
4.  [**03 | Parsing Pipeline Deep-Dive**](documentation/03_Parsing_Pipeline_Deep_Dive.md) - The 2-pass engine explained.
5.  [**05 | Threat Detection Heuristics**](documentation/05_Threat_Detection_Heuristics.md) - Behavioral analysis vs. virus databases.
6.  [**08 | Teaching Flow**](documentation/08_Teaching_Flow_Curriculum.md) - A guide for classroom instruction.

---

## 🚀 Key Features

### 🕵️ The Investigator (Parser)
- **2-Pass Pipeline**: Identifies conversations first, then analyzes protocol details.
- **Intelligent Linking**: Automatically correlates DNS queries with their resulting TCP/HTTP connections.
- **Unified Handlers**: Specialized "Experts" for DNS, HTTP, TLS, ICMP, and more.

### 🧠 The Security Guard (Threats)
- **Heuristic Engine**: Detects Port Scanning and DNS Tunneling via behavior, not just signatures.
- **Risk Scoring**: Calculates a math-based severity score (0-100) for every IP address.

### 🌍 The Global View (Geomap)
- **Dual-API strategy**: Uses `ipinfo.io` and `ip-api.com` to map attackers globally.
- **Interactive Leaflet Maps**: Real-world "pins" showing where traffic originates.

---

## ⚡ Quick Start

### 📦 Proper Installation (Package Mode)
```bash
# This uses our simplified setup.py to fetch everything automatically
pip install .
```

### 🏃 Run the Application
```bash
python run.py
```
The application will start on **http://localhost:5000**

---

## 📁 Project Architecture (The Engine Room)

The project follows a modular "Services" architecture for clarity:

```
PCAP-StoryTeller/
├── run.py                 # The Ignition Switch (Entry Point)
├── setup.py               # The Assembly Line (Installation)
├── documentation/         # The Classroom (Curriculum)
├── frontend/              # The Dashboard (User Interface)
└── backend/               # The Engine Room (Analysis)
    ├── app.py             # Application Factory
    ├── data/              # The Brain (Persistence & DataManager)
    ├── parsers/           # The Investigator (Packet Deep-Dive)
    │   ├── pcap_parser.py
    │   └── protocol_handlers.py
    └── services/          # Specialized Experts
        ├── threat_service.py
        ├── map_service.py
        └── report_generator.py
```

---

## 🔧 Supported Protocols

| Protocol | Status | Analogy |
|----------|--------|---------|
| **DNS** | ✅ Full | The Network Phonebook |
| **HTTP** | ✅ Full | Unencrypted Web Postcards |
| **HTTPS/TLS** | ✅ Full | Locked Safes (SNI detection) |
| **TCP** | ✅ Full | Registered Letters (Ordered) |
| **ICMP** | ✅ Full | Calling "Hello?" (Ping) |

---

## 🙏 Credits & Acknowledgments
Built for educators using these amazing open-source projects:
- [**Scapy**](https://scapy.readthedocs.io/) - The Magnifying Glass.
- [**Flask**](https://flask.palletsprojects.com/) - The Storytelling Engine.
- [**Folium**](https://python-visualization.github.io/folium/) - The Global Map.
- [**vis.js**](http://visjs.org/) & [**Chart.js**](https://www.chartjs.org/) - The Visuals.

---

**Made with ❤️ for students of Cybersecurity**
