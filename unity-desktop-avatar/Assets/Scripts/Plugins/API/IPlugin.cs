using System;
using System.Collections;
using UnityEngine;

namespace AvatarMCP.Plugins.API
{
    /// <summary>
    /// Base interface for all AvatarMCP plugins
    /// </summary>
    public interface IPlugin
    {
        /// <summary>
        /// Plugin metadata
        /// </summary>
        PluginInfo Info { get; }

        /// <summary>
        /// Plugin state
        /// </summary>
        PluginState State { get; }

        /// <summary>
        /// Initialize the plugin
        /// </summary>
        /// <param name="context">Plugin context with system access</param>
        void Initialize(PluginContext context);

        /// <summary>
        /// Start the plugin
        /// </summary>
        void Start();

        /// <summary>
        /// Update the plugin (called every frame)
        /// </summary>
        void Update();

        /// <summary>
        /// Late update the plugin (called after Update)
        /// </summary>
        void LateUpdate();

        /// <summary>
        /// Fixed update the plugin (called at fixed intervals)
        /// </summary>
        void FixedUpdate();

        /// <summary>
        /// Shutdown the plugin
        /// </summary>
        void Shutdown();

        /// <summary>
        /// Handle OSC message
        /// </summary>
        /// <param name="address">OSC address</param>
        /// <param name="values">OSC values</param>
        /// <returns>True if message was handled</returns>
        bool HandleOSCMessage(string address, object[] values);

        /// <summary>
        /// Get plugin settings UI (optional)
        /// </summary>
        /// <returns>Settings UI GameObject or null</returns>
        GameObject GetSettingsUI();
    }

    /// <summary>
    /// Plugin information
    /// </summary>
    [Serializable]
    public class PluginInfo
    {
        public string id;
        public string name;
        public string version;
        public string author;
        public string description;
        public string[] dependencies;
        public PluginCategory category;
        public PluginPermissions permissions;
    }

    /// <summary>
    /// Plugin categories
    /// </summary>
    public enum PluginCategory
    {
        Core,
        Animation,
        Expression,
        Movement,
        Interaction,
        Audio,
        Visual,
        Network,
        Utility,
        Experimental
    }

    /// <summary>
    /// Plugin permissions
    /// </summary>
    [Serializable]
    public class PluginPermissions
    {
        public bool canAccessAvatar = false;
        public bool canAccessOSC = false;
        public bool canAccessWindow = false;
        public bool canAccessFileSystem = false;
        public bool canAccessNetwork = false;
        public bool canExecuteCode = false;
    }

    /// <summary>
    /// Plugin states
    /// </summary>
    public enum PluginState
    {
        Unloaded,
        Loading,
        Loaded,
        Starting,
        Running,
        Stopping,
        Stopped,
        Error
    }

    /// <summary>
    /// Context provided to plugins for system access
    /// </summary>
    public class PluginContext
    {
        public AvatarMCP.Core.AvatarSystem AvatarSystem { get; private set; }
        public AvatarMCP.VRM.AvatarController AvatarController { get; private set; }
        public AvatarMCP.UI.Windows.WindowManager WindowManager { get; private set; }
        public AvatarMCP.Core.Network.OSCReceiver OSCReceiver { get; private set; }

        // Plugin-specific data storage
        private System.Collections.Generic.Dictionary<string, object> data =
            new System.Collections.Generic.Dictionary<string, object>();

        public PluginContext(
            AvatarMCP.Core.AvatarSystem avatarSystem,
            AvatarMCP.VRM.AvatarController avatarController,
            AvatarMCP.UI.Windows.WindowManager windowManager,
            AvatarMCP.Core.Network.OSCReceiver oscReceiver)
        {
            AvatarSystem = avatarSystem;
            AvatarController = avatarController;
            WindowManager = windowManager;
            OSCReceiver = oscReceiver;
        }

        /// <summary>
        /// Store plugin data
        /// </summary>
        public void SetData(string key, object value)
        {
            data[key] = value;
        }

        /// <summary>
        /// Retrieve plugin data
        /// </summary>
        public object GetData(string key)
        {
            return data.ContainsKey(key) ? data[key] : null;
        }

        /// <summary>
        /// Check if data exists
        /// </summary>
        public bool HasData(string key)
        {
            return data.ContainsKey(key);
        }

        /// <summary>
        /// Remove plugin data
        /// </summary>
        public void RemoveData(string key)
        {
            data.Remove(key);
        }
    }
}
