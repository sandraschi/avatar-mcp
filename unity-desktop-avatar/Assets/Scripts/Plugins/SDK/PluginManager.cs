using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEngine;
using AvatarMCP.Plugins.API;

namespace AvatarMCP.Plugins.SDK
{
    /// <summary>
    /// Manages loading, unloading, and lifecycle of plugins
    /// </summary>
    public class PluginManager : MonoBehaviour
    {
        [Header("Plugin Settings")]
        [SerializeField] private string pluginsPath = "StreamingAssets/Plugins";
        [SerializeField] private bool autoLoadPlugins = true;
        [SerializeField] private bool sandboxPlugins = true;

        // Plugin collections
        private Dictionary<string, IPlugin> loadedPlugins = new Dictionary<string, IPlugin>();
        private Dictionary<string, Assembly> loadedAssemblies = new Dictionary<string, Assembly>();
        private List<PluginInfo> availablePlugins = new List<PluginInfo>();

        // Plugin context
        private PluginContext pluginContext;

        // Events
        public event Action<IPlugin> OnPluginLoaded;
        public event Action<IPlugin> OnPluginStarted;
        public event Action<IPlugin> OnPluginStopped;
        public event Action<IPlugin> OnPluginUnloaded;
        public event Action<string> OnPluginError;

        private void Awake()
        {
            InitializePluginContext();
        }

        private void Start()
        {
            if (autoLoadPlugins)
            {
                StartCoroutine(LoadAllPluginsAsync());
            }
        }

        private void Update()
        {
            // Update all running plugins
            foreach (var plugin in loadedPlugins.Values)
            {
                if (plugin.State == PluginState.Running)
                {
                    try
                    {
                        plugin.Update();
                    }
                    catch (Exception ex)
                    {
                        HandlePluginError(plugin, $"Update error: {ex.Message}");
                    }
                }
            }
        }

        private void LateUpdate()
        {
            // Late update all running plugins
            foreach (var plugin in loadedPlugins.Values)
            {
                if (plugin.State == PluginState.Running)
                {
                    try
                    {
                        plugin.LateUpdate();
                    }
                    catch (Exception ex)
                    {
                        HandlePluginError(plugin, $"LateUpdate error: {ex.Message}");
                    }
                }
            }
        }

        private void FixedUpdate()
        {
            // Fixed update all running plugins
            foreach (var plugin in loadedPlugins.Values)
            {
                if (plugin.State == PluginState.Running)
                {
                    try
                    {
                        plugin.FixedUpdate();
                    }
                    catch (Exception ex)
                    {
                        HandlePluginError(plugin, $"FixedUpdate error: {ex.Message}");
                    }
                }
            }
        }

        private void OnDestroy()
        {
            UnloadAllPlugins();
        }

        #region Plugin Context

        private void InitializePluginContext()
        {
            // Find system components
            var avatarSystem = FindObjectOfType<AvatarMCP.Core.AvatarSystem>();
            AvatarMCP.VRM.AvatarController avatarController = null;
            AvatarMCP.UI.Windows.WindowManager windowManager = null;
            AvatarMCP.Core.Network.OSCReceiver oscReceiver = null;

            if (avatarSystem != null)
            {
                avatarController = avatarSystem.GetAvatarController();
                windowManager = avatarSystem.GetWindowManager();
                oscReceiver = avatarSystem.GetOSCReceiver();
            }

            pluginContext = new PluginContext(avatarSystem, avatarController, windowManager, oscReceiver);
        }

        #endregion

        #region Plugin Loading

        /// <summary>
        /// Load all available plugins
        /// </summary>
        public IEnumerator LoadAllPluginsAsync()
        {
            Debug.Log("Loading all plugins...");

            // Discover plugins
            yield return DiscoverPluginsAsync();

            // Load plugins with resolved dependencies
            var sortedPlugins = ResolveDependencies(availablePlugins);

            foreach (var pluginInfo in sortedPlugins)
            {
                yield return LoadPluginAsync(pluginInfo);
            }

            Debug.Log($"Loaded {loadedPlugins.Count} plugins");
        }

        /// <summary>
        /// Load a specific plugin
        /// </summary>
        public IEnumerator LoadPluginAsync(PluginInfo pluginInfo)
        {
            if (loadedPlugins.ContainsKey(pluginInfo.id))
            {
                Debug.LogWarning($"Plugin {pluginInfo.id} is already loaded");
                yield break;
            }

            try
            {
                Debug.Log($"Loading plugin: {pluginInfo.name} ({pluginInfo.id})");

                // Load assembly if needed
                Assembly assembly = LoadPluginAssembly(pluginInfo);
                if (assembly == null)
                {
                    HandlePluginError(null, $"Failed to load assembly for plugin {pluginInfo.id}");
                    yield break;
                }

                // Create plugin instance
                IPlugin plugin = CreatePluginInstance(assembly, pluginInfo);
                if (plugin == null)
                {
                    HandlePluginError(null, $"Failed to create instance for plugin {pluginInfo.id}");
                    yield break;
                }

                // Initialize plugin
                plugin.Initialize(pluginContext);

                // Register plugin
                loadedPlugins[pluginInfo.id] = plugin;
                loadedAssemblies[pluginInfo.id] = assembly;

                OnPluginLoaded?.Invoke(plugin);
                Debug.Log($"Plugin loaded successfully: {pluginInfo.name}");
            }
            catch (Exception ex)
            {
                HandlePluginError(null, $"Failed to load plugin {pluginInfo.id}: {ex.Message}");
            }

            yield return null;
        }

        /// <summary>
        /// Discover available plugins
        /// </summary>
        private IEnumerator DiscoverPluginsAsync()
        {
            availablePlugins.Clear();

            // Get plugin directory paths
            string[] pluginDirectories = GetPluginDirectories();

            foreach (string pluginDir in pluginDirectories)
            {
                PluginInfo pluginInfo = LoadPluginInfo(pluginDir);
                if (pluginInfo != null)
                {
                    availablePlugins.Add(pluginInfo);
                    Debug.Log($"Discovered plugin: {pluginInfo.name} v{pluginInfo.version}");
                }

                yield return null; // Allow other operations
            }
        }

        /// <summary>
        /// Load plugin info from manifest
        /// </summary>
        private PluginInfo LoadPluginInfo(string pluginDirectory)
        {
            try
            {
                string manifestPath = Path.Combine(pluginDirectory, "plugin.json");
                if (!File.Exists(manifestPath))
                {
                    return null;
                }

                string json = File.ReadAllText(manifestPath);
                return JsonUtility.FromJson<PluginInfo>(json);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load plugin info from {pluginDirectory}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get plugin directory paths
        /// </summary>
        private string[] GetPluginDirectories()
        {
            List<string> directories = new List<string>();

            // StreamingAssets plugins
            string streamingPath = Path.Combine(Application.streamingAssetsPath, "Plugins");
            if (Directory.Exists(streamingPath))
            {
                directories.AddRange(Directory.GetDirectories(streamingPath));
            }

            // Data path plugins
            string dataPath = Path.Combine(Application.dataPath, "Plugins");
            if (Directory.Exists(dataPath))
            {
                directories.AddRange(Directory.GetDirectories(dataPath));
            }

            return directories.ToArray();
        }

        /// <summary>
        /// Load plugin assembly
        /// </summary>
        private Assembly LoadPluginAssembly(PluginInfo pluginInfo)
        {
            try
            {
                // Try to load from various locations
                string[] possiblePaths = {
                    Path.Combine(Application.streamingAssetsPath, "Plugins", pluginInfo.id, $"{pluginInfo.id}.dll"),
                    Path.Combine(Application.dataPath, "Plugins", pluginInfo.id, $"{pluginInfo.id}.dll"),
                    $"{pluginInfo.id}.dll"
                };

                foreach (string dllPath in possiblePaths)
                {
                    if (File.Exists(dllPath))
                    {
                        return Assembly.LoadFile(dllPath);
                    }
                }

                // Try loading by name
                return Assembly.Load(pluginInfo.id);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load assembly for plugin {pluginInfo.id}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Create plugin instance from assembly
        /// </summary>
        private IPlugin CreatePluginInstance(Assembly assembly, PluginInfo pluginInfo)
        {
            try
            {
                // Find plugin class
                Type pluginType = assembly.GetTypes()
                    .FirstOrDefault(t => typeof(IPlugin).IsAssignableFrom(t) && !t.IsAbstract);

                if (pluginType == null)
                {
                    Debug.LogError($"No plugin class found in assembly {pluginInfo.id}");
                    return null;
                }

                // Create instance
                return (IPlugin)Activator.CreateInstance(pluginType);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create plugin instance {pluginInfo.id}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Resolve plugin dependencies
        /// </summary>
        private List<PluginInfo> ResolveDependencies(List<PluginInfo> plugins)
        {
            // Simple dependency resolution (could be enhanced)
            return plugins.OrderBy(p => p.dependencies?.Length ?? 0).ToList();
        }

        #endregion

        #region Plugin Management

        /// <summary>
        /// Start a plugin
        /// </summary>
        public void StartPlugin(string pluginId)
        {
            if (!loadedPlugins.TryGetValue(pluginId, out IPlugin plugin))
            {
                Debug.LogWarning($"Plugin {pluginId} is not loaded");
                return;
            }

            try
            {
                plugin.Start();
                OnPluginStarted?.Invoke(plugin);
                Debug.Log($"Plugin started: {plugin.Info.name}");
            }
            catch (Exception ex)
            {
                HandlePluginError(plugin, $"Start error: {ex.Message}");
            }
        }

        /// <summary>
        /// Stop a plugin
        /// </summary>
        public void StopPlugin(string pluginId)
        {
            if (!loadedPlugins.TryGetValue(pluginId, out IPlugin plugin))
            {
                Debug.LogWarning($"Plugin {pluginId} is not loaded");
                return;
            }

            try
            {
                plugin.Shutdown();
                OnPluginStopped?.Invoke(plugin);
                Debug.Log($"Plugin stopped: {plugin.Info.name}");
            }
            catch (Exception ex)
            {
                HandlePluginError(plugin, $"Stop error: {ex.Message}");
            }
        }

        /// <summary>
        /// Unload a plugin
        /// </summary>
        public void UnloadPlugin(string pluginId)
        {
            if (!loadedPlugins.TryGetValue(pluginId, out IPlugin plugin))
            {
                Debug.LogWarning($"Plugin {pluginId} is not loaded");
                return;
            }

            try
            {
                // Stop if running
                if (plugin.State == PluginState.Running)
                {
                    plugin.Shutdown();
                }

                loadedPlugins.Remove(pluginId);
                loadedAssemblies.Remove(pluginId);

                OnPluginUnloaded?.Invoke(plugin);
                Debug.Log($"Plugin unloaded: {plugin.Info.name}");
            }
            catch (Exception ex)
            {
                HandlePluginError(plugin, $"Unload error: {ex.Message}");
            }
        }

        /// <summary>
        /// Unload all plugins
        /// </summary>
        public void UnloadAllPlugins()
        {
            foreach (var pluginId in loadedPlugins.Keys.ToArray())
            {
                UnloadPlugin(pluginId);
            }
        }

        /// <summary>
        /// Start all loaded plugins
        /// </summary>
        public void StartAllPlugins()
        {
            foreach (var plugin in loadedPlugins.Values)
            {
                if (plugin.State == PluginState.Loaded)
                {
                    StartPlugin(plugin.Info.id);
                }
            }
        }

        /// <summary>
        /// Stop all running plugins
        /// </summary>
        public void StopAllPlugins()
        {
            foreach (var plugin in loadedPlugins.Values)
            {
                if (plugin.State == PluginState.Running)
                {
                    StopPlugin(plugin.Info.id);
                }
            }
        }

        #endregion

        #region Plugin Communication

        /// <summary>
        /// Handle OSC message for plugins
        /// </summary>
        public bool HandleOSCMessage(string address, object[] values)
        {
            foreach (var plugin in loadedPlugins.Values)
            {
                if (plugin.State == PluginState.Running)
                {
                    try
                    {
                        if (plugin.HandleOSCMessage(address, values))
                        {
                            return true; // Message handled
                        }
                    }
                    catch (Exception ex)
                    {
                        HandlePluginError(plugin, $"OSC handling error: {ex.Message}");
                    }
                }
            }

            return false; // Message not handled
        }

        #endregion

        #region Plugin Information

        /// <summary>
        /// Get loaded plugin by ID
        /// </summary>
        public IPlugin GetPlugin(string pluginId)
        {
            loadedPlugins.TryGetValue(pluginId, out IPlugin plugin);
            return plugin;
        }

        /// <summary>
        /// Get all loaded plugins
        /// </summary>
        public IPlugin[] GetAllPlugins()
        {
            return loadedPlugins.Values.ToArray();
        }

        /// <summary>
        /// Get available plugins
        /// </summary>
        public PluginInfo[] GetAvailablePlugins()
        {
            return availablePlugins.ToArray();
        }

        /// <summary>
        /// Check if plugin is loaded
        /// </summary>
        public bool IsPluginLoaded(string pluginId)
        {
            return loadedPlugins.ContainsKey(pluginId);
        }

        /// <summary>
        /// Check if plugin is running
        /// </summary>
        public bool IsPluginRunning(string pluginId)
        {
            if (loadedPlugins.TryGetValue(pluginId, out IPlugin plugin))
            {
                return plugin.State == PluginState.Running;
            }
            return false;
        }

        #endregion

        #region Error Handling

        private void HandlePluginError(IPlugin plugin, string error)
        {
            string pluginName = plugin != null ? plugin.Info.name : "Unknown Plugin";
            Debug.LogError($"Plugin error ({pluginName}): {error}");

            OnPluginError?.Invoke(error);

            // Mark plugin as error state if applicable
            if (plugin != null)
            {
                // Note: This would require adding a State setter to IPlugin
                // plugin.State = PluginState.Error;
            }
        }

        #endregion
    }
}
