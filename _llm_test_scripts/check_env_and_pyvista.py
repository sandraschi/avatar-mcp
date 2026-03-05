import platform
import sys


def check_python():
    print("=== Python Environment ===")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()} {platform.release()}")


def check_packages():
    print("\n=== Installed Packages ===")
    try:
        import pkg_resources

        packages = ["pyvista", "numpy", "matplotlib", "vtk"]
        for pkg in packages:
            try:
                version = pkg_resources.get_distribution(pkg).version
                print(f"{pkg}: {version}")
            except pkg_resources.DistributionNotFound:
                print(f"{pkg}: Not installed")
    except ImportError:
        print("Could not check packages - pkg_resources not available")


def check_opengl():
    print("\n=== OpenGL Information ===")
    try:
        from OpenGL import GL

        print(f"PyOpenGL version: {GL.__version__}")

        # Try to create an OpenGL context
        import glfw

        if not glfw.init():
            print("Failed to initialize GLFW")
            return

        # Set error callback
        def error_callback(error, description):
            print(f"GLFW Error {error}: {description}")

        glfw.set_error_callback(error_callback)

        # Create a windowed mode window and its OpenGL context
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)  # Don't show the window
        window = glfw.create_window(100, 100, "Test Window", None, None)
        if not window:
            print("Failed to create GLFW window")
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(window)

        # Get OpenGL version
        print(f"OpenGL Version: {GL.glGetString(GL.GL_VERSION).decode()}")
        print(f"OpenGL Vendor: {GL.glGetString(GL.GL_VENDOR).decode()}")
        print(f"OpenGL Renderer: {GL.glGetString(GL.GL_RENDERER).decode()}")

        # Clean up
        glfw.terminate()

    except ImportError as e:
        print(f"Could not check OpenGL: {e}")
    except Exception as e:
        print(f"Error checking OpenGL: {e}")


def main():
    check_python()
    check_packages()
    check_opengl()

    print("\n=== Test Complete ===")
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
