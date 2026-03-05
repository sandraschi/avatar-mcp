import logging
import sys


def test_logging():
    # Test basic logging
    print("Testing logging configuration...")
    print("This is a print statement to stdout", file=sys.stdout)
    print("This is a print statement to stderr", file=sys.stderr)

    # Test logging module
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    logger = logging.getLogger("test")
    logger.info("This is an INFO message")
    logger.error("This is an ERROR message")
    logger.debug("This is a DEBUG message (should not appear)")

    # Test file logging
    try:
        with open("test_log_output.txt", "w") as f:
            f.write("Test file write operation\n")
        print("Successfully wrote to test_log_output.txt")
    except Exception as e:
        print(f"Failed to write to file: {e}")


if __name__ == "__main__":
    test_logging()
