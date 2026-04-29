# 07 | 🔍 Search & Investigation

When a PCAP file has 10,000 packets, you need a way to find exactly what you are looking for.

---

## 🔎 The Search Engine
The search engine is simple but effective. It lets students filter by:
- **IP Address**: Show me only what `192.168.1.5` did.
- **Protocol**: Show me only the `DNS` queries.
- **Content**: Look for a specific word inside the descriptions.

---

## 🔄 Investigation Pipeline

```mermaid
graph LR
    A[Full Event List] --> B(Apply Filter)
    B --> C{Match Found?}
    C -- "Yes" --> D[Include in Results]
    C -- "No" --> E[Skip]
    D --> F[Display on Dashboard]
```

---

## 📂 Key Files
- `backend/services/search_service.py`: The filtering logic.
