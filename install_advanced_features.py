#!/usr/bin/env python3
"""
Installation script for AvatarMCP advanced features.
This script helps users install optional dependencies for enhanced functionality.
"""

import subprocess
import sys


def print_status(message, status="info"):
    """Print colored status messages."""
    colors = {
        "info": "\033[94m",  # Blue
        "success": "\033[92m",  # Green
        "warning": "\033[93m",  # Yellow
        "error": "\033[91m",  # Red
        "reset": "\033[0m",  # Reset
    }

    prefix = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}

    print(f"{colors.get(status, '')}{prefix.get(status, '')} {message}{colors['reset']}")


def check_dependency(package_name, import_name=None):
    """Check if a dependency is installed."""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Main installation script."""
    import argparse

    parser = argparse.ArgumentParser(description="Install AvatarMCP advanced features")
    parser.add_argument("--check-only", action="store_true", help="Only check current status")
    parser.add_argument(
        "--install",
        choices=["all", "viz", "ai", "audio", "cv"],
        help="Install specific feature set",
    )
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    print_status("AvatarMCP Advanced Features Installation", "info")
    print("=" * 60)

    # Define feature packages
    features = {
        "3D Visualization": {
            "packages": ["pyvista>=0.35.0", "vtk", "numpy>=1.20.0"],
            "test_imports": ["pyvista", "vtk", "numpy"],
            "description": "3D avatar visualization and rendering",
            "key": "viz",
        },
        "AI/ML Features": {
            "packages": ["torch", "transformers", "sentence-transformers"],
            "test_imports": ["torch", "transformers", "sentence_transformers"],
            "description": "AI-powered motion generation and processing",
            "key": "ai",
        },
        "Audio Processing": {
            "packages": ["pyaudio", "SpeechRecognition", "pyttsx3", "gTTS"],
            "test_imports": ["pyaudio", "speech_recognition", "pyttsx3", "gtts"],
            "description": "Voice chat and audio processing",
            "key": "audio",
        },
        "Computer Vision": {
            "packages": ["opencv-python", "mediapipe", "Pillow"],
            "test_imports": ["cv2", "mediapipe", "PIL"],
            "description": "Computer vision and image processing",
            "key": "cv",
        },
    }

    # Check current status
    print_status("Checking current environment...", "info")
    print("\nCurrent Feature Status:")
    print("-" * 40)

    available_features = {}
    for feature_name, feature_info in features.items():
        all_available = all(
            check_dependency(pkg.split(">=")[0], imp)
            for pkg, imp in zip(feature_info["packages"], feature_info["test_imports"], strict=False)
        )
        available_features[feature_name] = all_available

        if all_available:
            print_status(f"{feature_name}: Available", "success")
        else:
            missing = [
                pkg.split(">=")[0]
                for pkg, imp in zip(feature_info["packages"], feature_info["test_imports"], strict=False)
                if not check_dependency(pkg.split(">=")[0], imp)
            ]
            print_status(f"{feature_name}: Missing ({', '.join(missing)})", "warning")

    # Handle command line arguments
    if args.check_only:
        print_status("Requirements check completed", "info")
        return

    if args.install:
        if args.install == "all":
            install_all_features(features)
        else:
            install_specific_feature(features, args.install)
        return

    # Interactive mode or default behavior
    if args.interactive or (not args.check_only and not args.install):
        run_interactive_mode(features)


def install_all_features(features):
    """Install all features."""
    print_status("Installing all advanced features...", "info")
    for feature_name, feature_info in features.items():
        print_status(f"Installing {feature_name}...", "info")
        for package in feature_info["packages"]:
            if install_package(package):
                print_status(f"  ✓ {package}", "success")
            else:
                print_status(f"  ✗ {package}", "error")
    show_completion_message()


def install_specific_feature(features, feature_key):
    """Install a specific feature."""
    feature_map = {info["key"]: (name, info) for name, info in features.items()}

    if feature_key not in feature_map:
        print_status(f"Unknown feature key: {feature_key}", "error")
        return

    feature_name, feature_info = feature_map[feature_key]
    print_status(f"Installing {feature_name}...", "info")

    for package in feature_info["packages"]:
        if install_package(package):
            print_status(f"  ✓ {package}", "success")
        else:
            print_status(f"  ✗ {package}", "error")
    show_completion_message()


def run_interactive_mode(features):
    """Run interactive installation mode."""
    try:
        print("\n" + "=" * 60)
        print("Installation Options:")
        print("1. Install all features")
        print("2. Install specific features")
        print("3. Check requirements only")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            install_all_features(features)

        elif choice == "2":
            print("\nAvailable Features:")
            for i, (feature_name, feature_info) in enumerate(features.items(), 1):
                print(f"{i}. {feature_name} - {feature_info['description']}")

            selected = input("\nEnter feature numbers (comma-separated): ").strip()
            try:
                indices = [int(x.strip()) - 1 for x in selected.split(",")]
                feature_list = list(features.items())

                for idx in indices:
                    if 0 <= idx < len(feature_list):
                        feature_name, feature_info = feature_list[idx]
                        print_status(f"Installing {feature_name}...", "info")
                        for package in feature_info["packages"]:
                            if install_package(package):
                                print_status(f"  ✓ {package}", "success")
                            else:
                                print_status(f"  ✗ {package}", "error")
                show_completion_message()
            except ValueError:
                print_status("Invalid selection", "error")

        elif choice == "3":
            print_status("Requirements check completed (see above)", "info")

        elif choice == "4":
            print_status("Installation cancelled", "info")
            return

        else:
            print_status("Invalid choice", "error")
            return

    except (KeyboardInterrupt, EOFError):
        print_status("\nInstallation cancelled by user", "warning")
        return


def show_completion_message():
    """Show completion message with next steps."""
    print("\n" + "=" * 60)
    print_status("Installation completed!", "success")
    print("\nTo use advanced features:")
    print("1. Update your Claude Desktop configuration to use the enhanced server:")
    print("   Change: python src/avatarmcp/mcp_main.py")
    print("   To:     python src/avatarmcp/mcp_enhanced.py")
    print("2. Restart Claude Desktop")
    print("3. Use the 'system.capabilities' tool to check available features")
    print("\nCommand line usage:")
    print("  python install_advanced_features.py --check-only")
    print("  python install_advanced_features.py --install all")
    print("  python install_advanced_features.py --install viz")
    print("  python install_advanced_features.py --interactive")


if __name__ == "__main__":
    main()
