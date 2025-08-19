using UnityEngine;
using System.Runtime.InteropServices;

public class WindowManager : SingletonMonoBehaviour<WindowManager>
{
    #region DLL Imports
    
    [DllImport("user32.dll")]
    private static extern IntPtr GetActiveWindow();
    
    [DllImport("user32.dll")]
    private static extern int SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);
    
    [DllImport("user32.dll")]
    private static extern bool SetWindowPos(IntPtr hWnd, int hWndInsertAfter, int x, int y, int cx, int cy, uint uFlags);
    
    [DllImport("Dwmapi.dll")]
    private static extern uint DwmExtendFrameIntoClientArea(IntPtr hWnd, ref MARGINS margins);
    
    #endregion
    
    #region Structs
    
    private struct MARGINS
    {
        public int cxLeftWidth;
        public int cxRightWidth;
        public int cyTopHeight;
        public int cyBottomHeight;
    }
    
    #endregion
    
    #region Public Fields
    
    [Header("Window Settings")]
    public bool alwaysOnTop = true;
    public bool clickThrough = false;
    public Vector2Int position = new Vector2Int(0, 0);
    public Vector2Int size = new Vector2Int(800, 600);
    
    #endregion
    
    #region Private Fields
    
    private const int GWL_STYLE = -16;
    private const uint WS_POPUP = 0x80000000;
    private const uint WS_VISIBLE = 0x10000000;
    private const uint WS_EX_LAYERED = 0x00080000;
    private const uint WS_EX_TRANSPARENT = 0x00000020;
    private const uint SWP_FRAMECHANGED = 0x0020;
    private const uint SWP_SHOWWINDOW = 0x0040;
    
    #endregion
    
    #region Unity Methods
    
    private void Start()
    {
        #if !UNITY_EDITOR && UNITY_STANDALONE_WIN
        SetupWindow();
        #endif
    }
    
    #endregion
    
    #region Public Methods
    
    public void SetWindowPosition(Vector2Int newPosition)
    {
        position = newPosition;
        UpdateWindowPosition();
    }
    
    public void SetWindowSize(Vector2Int newSize)
    {
        size = newSize;
        UpdateWindowPosition();
    }
    
    #endregion
    
    #region Private Methods
    
    private void SetupWindow()
    {
        var windowHandle = GetActiveWindow();
        
        // Set window style
        uint style = WS_POPUP | WS_VISIBLE;
        SetWindowLong(windowHandle, GWL_STYLE, style);
        
        // Set window position and size
        UpdateWindowPosition();
        
        // Make window transparent
        MARGINS margins = new MARGINS { cxLeftWidth = -1 };
        DwmExtendFrameIntoClientArea(windowHandle, ref margins);
        
        // Set click-through if enabled
        if (clickThrough)
        {
            var extendedStyle = WS_EX_LAYERED | WS_EX_TRANSPARENT;
            SetWindowLong(windowHandle, -20, extendedStyle);
        }
    }
    
    private void UpdateWindowPosition()
    {
        var windowHandle = GetActiveWindow();
        SetWindowPos(
            windowHandle,
            0,
            position.x,
            position.y,
            size.x,
            size.y,
            SWP_SHOWWINDOW | SWP_FRAMECHANGED
        );
    }
    
    #endregion
}
