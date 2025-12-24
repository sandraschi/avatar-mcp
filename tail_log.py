def tail_log(file_path, num_lines=20):
    try:
        # Read the last N lines from the file
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            # Get the last N lines efficiently
            lines = f.readlines()[-num_lines:]

        # Print the file path and last N lines
        print(f"Last {len(lines)} lines of: {file_path}")
        print("-" * 80)
        print("".join(lines), end="")
        print("-" * 80)

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"Error reading log file: {e}")


if __name__ == "__main__":
    log_path = r"C:\Users\sandr\AppData\Roaming\Claude\logs\mcp-server-avatarmcp.log"
    tail_log(log_path)
