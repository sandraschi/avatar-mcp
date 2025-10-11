using System;
using System.Runtime.InteropServices;
using UnityEngine;

namespace AvatarMCP.UI.Windows
{
    /// <summary>
    /// Manages transparent desktop window for avatar overlay
    /// </summary>
    public class WindowManager : MonoBehaviour
    {
        [Header("Window Settings")]
        [SerializeField] private int windowWidth = 800;
        [SerializeField] private int windowHeight = 1200;
        [SerializeField] private bool startTransparent = true;
        [SerializeField] private bool startClickThrough = false;
        [SerializeField] private bool startAlwaysOnTop = true;
        [SerializeField] private bool startBorderless = true;

        // Window state
        private bool isTransparent = false;
        private bool isClickThrough = false;
        private bool isAlwaysOnTop = false;
        private bool isBorderless = false;
        private IntPtr windowHandle;

        // Events
        public event Action OnWindowStateChanged;

        private void Start()
        {
            // Initialize window
            InitializeWindow();

            // Set initial state
            if (startTransparent) SetTransparency(true);
            if (startClickThrough) SetClickThrough(true);
            if (startAlwaysOnTop) SetAlwaysOnTop(true);
            if (startBorderless) SetBorderless(true);
        }

        private void Update()
        {
            // Handle window messages and updates
            ProcessWindowMessages();
        }

        private void OnDestroy()
        {
            // Restore window state
            RestoreWindowState();
        }

        #region Window Initialization

        private void InitializeWindow()
        {
            // Get window handle
            windowHandle = GetWindowHandle();

            if (windowHandle == IntPtr.Zero)
            {
                Debug.LogError("Failed to get window handle");
                return;
            }

            Debug.Log($"Window initialized: {windowHandle}");
        }

        private IntPtr GetWindowHandle()
        {
            #if UNITY_STANDALONE_WIN
            return GetActiveWindow();
            #else
            return IntPtr.Zero;
            #endif
        }

        #endregion

        #region Transparency Control

        /// <summary>
        /// Set window transparency
        /// </summary>
        public void SetTransparency(bool transparent)
        {
            if (isTransparent == transparent) return;

            isTransparent = transparent;

            #if UNITY_STANDALONE_WIN
            if (transparent)
            {
                // Make window transparent
                int extendedStyle = GetWindowLong(windowHandle, GWL_EXSTYLE);
                SetWindowLong(windowHandle, GWL_EXSTYLE, extendedStyle | WS_EX_LAYERED | WS_EX_TRANSPARENT);

                // Set transparency level (0 = fully transparent, 255 = opaque)
                SetLayeredWindowAttributes(windowHandle, 0, 128, LWA_ALPHA);
            }
            else
            {
                // Restore normal window
                int extendedStyle = GetWindowLong(windowHandle, GWL_EXSTYLE);
                SetWindowLong(windowHandle, GWL_EXSTYLE, extendedStyle & ~(WS_EX_LAYERED | WS_EX_TRANSPARENT));
            }
            #endif

            OnWindowStateChanged?.Invoke();
            Debug.Log($"Window transparency set to: {transparent}");
        }

        /// <summary>
        /// Get current transparency state
        /// </summary>
        public bool GetTransparency()
        {
            return isTransparent;
        }

        /// <summary>
        /// Set transparency level (0.0 = fully transparent, 1.0 = opaque)
        /// </summary>
        public void SetTransparencyLevel(float level)
        {
            level = Mathf.Clamp01(level);
            byte alpha = (byte)(level * 255);

            #if UNITY_STANDALONE_WIN
            SetLayeredWindowAttributes(windowHandle, 0, alpha, LWA_ALPHA);
            #endif

            Debug.Log($"Window transparency level set to: {level}");
        }

        #endregion

        #region Click-Through Control

        /// <summary>
        /// Set window click-through mode
        /// </summary>
        public void SetClickThrough(bool clickThrough)
        {
            if (isClickThrough == clickThrough) return;

            isClickThrough = clickThrough;

            #if UNITY_STANDALONE_WIN
            if (clickThrough)
            {
                // Make window click-through
                int extendedStyle = GetWindowLong(windowHandle, GWL_EXSTYLE);
                SetWindowLong(windowHandle, GWL_EXSTYLE, extendedStyle | WS_EX_TRANSPARENT);
            }
            else
            {
                // Restore normal window
                int extendedStyle = GetWindowLong(windowHandle, GWL_EXSTYLE);
                SetWindowLong(windowHandle, GWL_EXSTYLE, extendedStyle & ~WS_EX_TRANSPARENT);
            }
            #endif

            OnWindowStateChanged?.Invoke();
            Debug.Log($"Window click-through set to: {clickThrough}");
        }

        /// <summary>
        /// Get current click-through state
        /// </summary>
        public bool GetClickThrough()
        {
            return isClickThrough;
        }

        #endregion

        #region Always-on-Top Control

        /// <summary>
        /// Set window always-on-top mode
        /// </summary>
        public void SetAlwaysOnTop(bool alwaysOnTop)
        {
            if (isAlwaysOnTop == alwaysOnTop) return;

            isAlwaysOnTop = alwaysOnTop;

            #if UNITY_STANDALONE_WIN
            if (alwaysOnTop)
            {
                SetWindowPos(windowHandle, HWND_TOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
            }
            else
            {
                SetWindowPos(windowHandle, HWND_NOTOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
            }
            #endif

            OnWindowStateChanged?.Invoke();
            Debug.Log($"Window always-on-top set to: {alwaysOnTop}");
        }

        /// <summary>
        /// Get current always-on-top state
        /// </summary>
        public bool GetAlwaysOnTop()
        {
            return isAlwaysOnTop;
        }

        #endregion

        #region Border Control

        /// <summary>
        /// Set window borderless mode
        /// </summary>
        public void SetBorderless(bool borderless)
        {
            if (isBorderless == borderless) return;

            isBorderless = borderless;

            #if UNITY_STANDALONE_WIN
            if (borderless)
            {
                // Remove window borders and title bar
                int style = GetWindowLong(windowHandle, GWL_STYLE);
                style &= ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU);
                SetWindowLong(windowHandle, GWL_STYLE, style);

                // Update window
                SetWindowPos(windowHandle, IntPtr.Zero, 0, 0, windowWidth, windowHeight,
                    SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE);
            }
            else
            {
                // Restore window borders
                int style = GetWindowLong(windowHandle, GWL_STYLE);
                style |= WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU;
                SetWindowLong(windowHandle, GWL_STYLE, style);

                // Update window
                SetWindowPos(windowHandle, IntPtr.Zero, 0, 0, windowWidth, windowHeight,
                    SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE);
            }
            #endif

            OnWindowStateChanged?.Invoke();
            Debug.Log($"Window borderless set to: {borderless}");
        }

        /// <summary>
        /// Get current borderless state
        /// </summary>
        public bool GetBorderless()
        {
            return isBorderless;
        }

        #endregion

        #region Positioning and Sizing

        /// <summary>
        /// Set window position
        /// </summary>
        public void SetPosition(int x, int y)
        {
            #if UNITY_STANDALONE_WIN
            SetWindowPos(windowHandle, IntPtr.Zero, x, y, 0, 0,
                SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE);
            #endif

            Debug.Log($"Window position set to: ({x}, {y})");
        }

        /// <summary>
        /// Set window size
        /// </summary>
        public void SetSize(int width, int height)
        {
            windowWidth = width;
            windowHeight = height;

            #if UNITY_STANDALONE_WIN
            SetWindowPos(windowHandle, IntPtr.Zero, 0, 0, width, height,
                SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE);
            #endif

            Debug.Log($"Window size set to: {width}x{height}");
        }

        /// <summary>
        /// Move window relative to current position
        /// </summary>
        public void MoveRelative(int dx, int dy)
        {
            #if UNITY_STANDALONE_WIN
            RECT rect;
            GetWindowRect(windowHandle, out rect);
            SetPosition(rect.left + dx, rect.top + dy);
            #endif
        }

        /// <summary>
        /// Center window on screen
        /// </summary>
        public void CenterOnScreen()
        {
            #if UNITY_STANDALONE_WIN
            int screenWidth = Screen.currentResolution.width;
            int screenHeight = Screen.currentResolution.height;
            int x = (screenWidth - windowWidth) / 2;
            int y = (screenHeight - windowHeight) / 2;
            SetPosition(x, y);
            #endif
        }

        /// <summary>
        /// Move window to specific monitor
        /// </summary>
        public void MoveToMonitor(int monitorIndex)
        {
            #if UNITY_STANDALONE_WIN
            var monitors = GetMonitors();
            if (monitorIndex >= 0 && monitorIndex < monitors.Length)
            {
                var monitor = monitors[monitorIndex];
                int x = monitor.left + (monitor.right - monitor.left - windowWidth) / 2;
                int y = monitor.top + (monitor.bottom - monitor.top - windowHeight) / 2;
                SetPosition(x, y);
            }
            #endif
        }

        #endregion

        #region Window State Management

        /// <summary>
        /// Bring window to front
        /// </summary>
        public void BringToFront()
        {
            #if UNITY_STANDALONE_WIN
            SetForegroundWindow(windowHandle);
            #endif
        }

        /// <summary>
        /// Minimize window
        /// </summary>
        public void Minimize()
        {
            #if UNITY_STANDALONE_WIN
            ShowWindow(windowHandle, SW_MINIMIZE);
            #endif
        }

        /// <summary>
        /// Maximize window
        /// </summary>
        public void Maximize()
        {
            #if UNITY_STANDALONE_WIN
            ShowWindow(windowHandle, SW_MAXIMIZE);
            #endif
        }

        /// <summary>
        /// Restore window
        /// </summary>
        public void Restore()
        {
            #if UNITY_STANDALONE_WIN
            ShowWindow(windowHandle, SW_RESTORE);
            #endif
        }

        /// <summary>
        /// Close window
        /// </summary>
        public void Close()
        {
            #if UNITY_STANDALONE_WIN
            SendMessage(windowHandle, WM_CLOSE, IntPtr.Zero, IntPtr.Zero);
            #endif
        }

        #endregion

        #region Private Methods

        private void ProcessWindowMessages()
        {
            // Handle any pending window messages
            // This is typically handled by Unity's message pump
        }

        private void RestoreWindowState()
        {
            // Restore normal window state on exit
            SetTransparency(false);
            SetClickThrough(false);
            SetAlwaysOnTop(false);
            SetBorderless(false);
        }

        private MONITORINFO[] GetMonitors()
        {
            // Implementation for getting monitor information
            // This would require additional Win32 API calls
            return new MONITORINFO[0];
        }

        #endregion

        #region Win32 API Declarations

        #if UNITY_STANDALONE_WIN
        [DllImport("user32.dll")]
        private static extern IntPtr GetActiveWindow();

        [DllImport("user32.dll")]
        private static extern int GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll")]
        private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

        [DllImport("user32.dll")]
        private static extern bool SetLayeredWindowAttributes(IntPtr hWnd, uint crKey, byte bAlpha, uint dwFlags);

        [DllImport("user32.dll")]
        private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

        [DllImport("user32.dll")]
        private static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

        [DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        [DllImport("user32.dll")]
        private static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        // Constants
        private const int GWL_STYLE = -16;
        private const int GWL_EXSTYLE = -20;
        private const uint WS_EX_LAYERED = 0x00080000;
        private const uint WS_EX_TRANSPARENT = 0x00000020;
        private const uint LWA_ALPHA = 0x00000002;
        private const uint WS_CAPTION = 0x00C00000;
        private const uint WS_THICKFRAME = 0x00040000;
        private const uint WS_MINIMIZEBOX = 0x00020000;
        private const uint WS_MAXIMIZEBOX = 0x00010000;
        private const uint WS_SYSMENU = 0x00080000;
        private const uint SWP_NOMOVE = 0x0002;
        private const uint SWP_NOSIZE = 0x0001;
        private const uint SWP_NOACTIVATE = 0x0010;
        private const uint SWP_FRAMECHANGED = 0x0020;
        private const uint SWP_NOZORDER = 0x0004;
        private static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
        private static readonly IntPtr HWND_NOTOPMOST = new IntPtr(-2);
        private const int SW_MINIMIZE = 6;
        private const int SW_MAXIMIZE = 3;
        private const int SW_RESTORE = 9;
        private const uint WM_CLOSE = 0x0010;

        [StructLayout(LayoutKind.Sequential)]
        public struct RECT
        {
            public int left;
            public int top;
            public int right;
            public int bottom;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct MONITORINFO
        {
            public int cbSize;
            public RECT rcMonitor;
            public RECT rcWork;
            public uint dwFlags;

            public int left => rcMonitor.left;
            public int top => rcMonitor.top;
            public int right => rcMonitor.right;
            public int bottom => rcMonitor.bottom;
        }
        #endif

        #endregion
    }
}
