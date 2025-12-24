log_path = r"C:\Users\sandr\AppData\Roaming\Claude\logs\mcp-server-avatarmcp.log"
try:
    with open(log_path, encoding="utf-8") as f:
        content = f.read()
        print(f"Log file contents (first 1000 chars):\n{content[:1000]}")
        print(f"\nTotal length: {len(content)} characters")
except FileNotFoundError:
    print(f"Error: File not found at {log_path}")
except Exception as e:
    print(f"Error reading log file: {e}")
