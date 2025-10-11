using System;
using System.Collections;
using UnityEngine;
using AvatarMCP.VRM;
using AvatarMCP.UI.Windows;
using AvatarMCP.Core.Network;

namespace AvatarMCP.Core
{
    /// <summary>
    /// Main system that coordinates all avatar functionality
    /// </summary>
    public class AvatarSystem : MonoBehaviour
    {
        [Header("Core Components")]
        [SerializeField] private VRMLoader vrmLoader;
        [SerializeField] private AvatarController avatarController;
        [SerializeField] private WindowManager windowManager;
        [SerializeField] private OSCReceiver oscReceiver;

        [Header("Configuration")]
        [SerializeField] private string configFilePath = "Resources/Config/config.json";
        [SerializeField] private bool loadConfigOnStart = true;

        // System state
        private bool isInitialized = false;
        private AvatarSystemConfig config;

        // Events
        public event Action OnSystemInitialized;
        public event Action OnSystemShutdown;

        private void Awake()
        {
            InitializeComponents();
        }

        private void Start()
        {
            StartCoroutine(InitializeSystemAsync());
        }

        private void OnDestroy()
        {
            ShutdownSystem();
        }

        #region System Initialization

        private void InitializeComponents()
        {
            // Find or create components
            if (vrmLoader == null)
            {
                vrmLoader = gameObject.AddComponent<VRMLoader>();
            }

            if (avatarController == null)
            {
                avatarController = gameObject.AddComponent<AvatarController>();
            }

            if (windowManager == null)
            {
                windowManager = gameObject.AddComponent<WindowManager>();
            }

            if (oscReceiver == null)
            {
                oscReceiver = gameObject.AddComponent<OSCReceiver>();
            }

            // Connect component references
            avatarController.vrmLoader = vrmLoader;
            oscReceiver.avatarController = avatarController;
            oscReceiver.windowManager = windowManager;

            Debug.Log("Components initialized");
        }

        private IEnumerator InitializeSystemAsync()
        {
            Debug.Log("Initializing AvatarMCP System...");

            // Load configuration
            if (loadConfigOnStart)
            {
                yield return LoadConfigurationAsync();
            }

            // Initialize OSC system
            if (oscReceiver != null)
            {
                oscReceiver.StartOSC();
            }

            // Wait for OSC to be ready
            yield return new WaitForSeconds(0.5f);

            isInitialized = true;
            OnSystemInitialized?.Invoke();

            Debug.Log("AvatarMCP System initialized successfully");
        }

        private IEnumerator LoadConfigurationAsync()
        {
            try
            {
                // Load config from Resources
                TextAsset configAsset = Resources.Load<TextAsset>("Config/config");
                if (configAsset != null)
                {
                    config = JsonUtility.FromJson<AvatarSystemConfig>(configAsset.text);
                    ApplyConfiguration(config);
                    Debug.Log("Configuration loaded from Resources");
                }
                else
                {
                    // Create default configuration
                    config = CreateDefaultConfig();
                    Debug.Log("Using default configuration");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load configuration: {ex.Message}");
                config = CreateDefaultConfig();
            }

            yield return null;
        }

        private void ApplyConfiguration(AvatarSystemConfig config)
        {
            // Apply window settings
            if (windowManager != null)
            {
                windowManager.SetSize(config.window.width, config.window.height);
                windowManager.SetPosition(config.window.position.x, config.window.position.y);
                windowManager.SetTransparency(config.window.transparent);
                windowManager.SetClickThrough(config.window.clickThrough);
                windowManager.SetAlwaysOnTop(config.window.alwaysOnTop);
                windowManager.SetBorderless(!config.window.border);
            }

            // Apply avatar settings
            if (avatarController != null)
            {
                avatarController.SetScale(config.avatar.scale);
                avatarController.SetVisibility(config.avatar.autoLoad);

                if (config.avatar.autoLoad && !string.IsNullOrEmpty(config.avatar.defaultPath))
                {
                    avatarController.LoadAvatar(config.avatar.defaultPath);
                }
            }

            // Apply OSC settings
            if (oscReceiver != null)
            {
                // OSC settings would be applied here if configurable
            }

            // Apply performance settings
            Application.targetFrameRate = config.performance.targetFPS;

            Debug.Log("Configuration applied");
        }

        private AvatarSystemConfig CreateDefaultConfig()
        {
            return new AvatarSystemConfig
            {
                window = new WindowConfig
                {
                    width = 800,
                    height = 1200,
                    transparent = true,
                    clickThrough = false,
                    alwaysOnTop = true,
                    position = new Vector2Int(100, 100)
                },
                avatar = new AvatarConfig
                {
                    defaultPath = "StreamingAssets/Avatars/default.vrm",
                    scale = 1.0f,
                    autoLoad = true
                },
                osc = new OSCConfig
                {
                    enabled = true,
                    port = 9000,
                    address = "127.0.0.1"
                },
                performance = new PerformanceConfig
                {
                    targetFPS = 60,
                    vSyncCount = 1,
                    physicsRate = 0.02f
                }
            };
        }

        #endregion

        #region System Management

        /// <summary>
        /// Initialize the system manually
        /// </summary>
        public void Initialize()
        {
            if (!isInitialized)
            {
                StartCoroutine(InitializeSystemAsync());
            }
        }

        /// <summary>
        /// Shutdown the system
        /// </summary>
        public void Shutdown()
        {
            ShutdownSystem();
        }

        private void ShutdownSystem()
        {
            OnSystemShutdown?.Invoke();

            // Stop OSC
            if (oscReceiver != null)
            {
                oscReceiver.StopOSC();
            }

            // Unload avatar
            if (avatarController != null)
            {
                avatarController.UnloadAvatar();
            }

            isInitialized = false;
            Debug.Log("AvatarMCP System shutdown");
        }

        /// <summary>
        /// Get system status
        /// </summary>
        public SystemStatus GetStatus()
        {
            return new SystemStatus
            {
                isInitialized = isInitialized,
                hasAvatar = avatarController != null && avatarController.HasAvatar(),
                oscConnected = oscReceiver != null && oscReceiver.IsConnected(),
                oscStatus = oscReceiver != null ? oscReceiver.GetStatus() : "Not available",
                windowTransparent = windowManager != null && windowManager.GetTransparency(),
                windowClickThrough = windowManager != null && windowManager.GetClickThrough(),
                windowAlwaysOnTop = windowManager != null && windowManager.GetAlwaysOnTop(),
                avatarVisible = avatarController != null && avatarController.GetVisibility()
            };
        }

        /// <summary>
        /// Save current configuration
        /// </summary>
        public void SaveConfiguration()
        {
            if (config == null) return;

            try
            {
                // Update config with current values
                if (windowManager != null)
                {
                    // Note: Getting current window position/size would require additional Win32 calls
                    config.window.transparent = windowManager.GetTransparency();
                    config.window.clickThrough = windowManager.GetClickThrough();
                    config.window.alwaysOnTop = windowManager.GetAlwaysOnTop();
                    config.window.border = !windowManager.GetBorderless();
                }

                if (avatarController != null)
                {
                    config.avatar.autoLoad = avatarController.GetVisibility();
                }

                // Save to file (would require additional file I/O implementation)
                string configJson = JsonUtility.ToJson(config, true);
                Debug.Log($"Configuration saved: {configJson}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to save configuration: {ex.Message}");
            }
        }

        /// <summary>
        /// Reset system to default state
        /// </summary>
        public void ResetToDefaults()
        {
            config = CreateDefaultConfig();
            ApplyConfiguration(config);
            Debug.Log("System reset to defaults");
        }

        #endregion

        #region Public API

        /// <summary>
        /// Get the avatar controller
        /// </summary>
        public AvatarController GetAvatarController()
        {
            return avatarController;
        }

        /// <summary>
        /// Get the window manager
        /// </summary>
        public WindowManager GetWindowManager()
        {
            return windowManager;
        }

        /// <summary>
        /// Get the OSC receiver
        /// </summary>
        public OSCReceiver GetOSCReceiver()
        {
            return oscReceiver;
        }

        /// <summary>
        /// Get the VRM loader
        /// </summary>
        public VRMLoader GetVRMLoader()
        {
            return vrmLoader;
        }

        #endregion
    }

    #region Configuration Classes

    [Serializable]
    public class AvatarSystemConfig
    {
        public WindowConfig window;
        public AvatarConfig avatar;
        public OSCConfig osc;
        public PerformanceConfig performance;
    }

    [Serializable]
    public class WindowConfig
    {
        public int width = 800;
        public int height = 1200;
        public bool transparent = true;
        public bool clickThrough = false;
        public bool alwaysOnTop = true;
        public bool border = false;
        public Vector2Int position;
    }

    [Serializable]
    public class AvatarConfig
    {
        public string defaultPath = "StreamingAssets/Avatars/default.vrm";
        public float scale = 1.0f;
        public bool autoLoad = true;
    }

    [Serializable]
    public class OSCConfig
    {
        public bool enabled = true;
        public int port = 9000;
        public string address = "127.0.0.1";
    }

    [Serializable]
    public class PerformanceConfig
    {
        public int targetFPS = 60;
        public int vSyncCount = 1;
        public float physicsRate = 0.02f;
    }

    #endregion

    #region Status Classes

    [Serializable]
    public class SystemStatus
    {
        public bool isInitialized;
        public bool hasAvatar;
        public bool oscConnected;
        public string oscStatus;
        public bool windowTransparent;
        public bool windowClickThrough;
        public bool windowAlwaysOnTop;
        public bool avatarVisible;
    }

    #endregion
}
