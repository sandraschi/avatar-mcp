using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using VRM;
using AvatarMCP.VRM;

namespace AvatarMCP.Core.Network
{
    /// <summary>
    /// Receives OSC messages for real-time avatar control
    /// </summary>
    public class OSCReceiver : MonoBehaviour
    {
        [Header("OSC Settings")]
        [SerializeField] private string localAddress = "127.0.0.1";
        [SerializeField] private int localPort = 9000;
        [SerializeField] private bool autoStart = true;

        [Header("Avatar Control")]
        [SerializeField] private AvatarController avatarController;
        [SerializeField] private WindowManager windowManager;

        // OSC components
        private extOSC.OSCReceiver receiver;
        private extOSC.OSCBindBundle bindBundle;

        // OSC address constants
        private const string AVATAR_BASE = "/avatar";
        private const string WINDOW_BASE = "/window";
        private const string SYSTEM_BASE = "/system";

        private void Awake()
        {
            InitializeOSC();
        }

        private void Start()
        {
            if (autoStart)
            {
                StartOSC();
            }

            // Find components if not assigned
            if (avatarController == null)
            {
                avatarController = FindObjectOfType<AvatarController>();
            }

            if (windowManager == null)
            {
                windowManager = FindObjectOfType<WindowManager>();
            }
        }

        private void OnDestroy()
        {
            StopOSC();
        }

        #region OSC Initialization

        private void InitializeOSC()
        {
            // Create OSC receiver
            receiver = gameObject.AddComponent<extOSC.OSCReceiver>();
            receiver.LocalHost = localAddress;
            receiver.LocalPort = localPort;

            // Create bind bundle
            bindBundle = new extOSC.OSCBindBundle();

            // Bind avatar controls
            BindAvatarControls();

            // Bind window controls
            BindWindowControls();

            // Bind system controls
            BindSystemControls();

            // Apply bindings
            receiver.Bind(bindBundle);

            Debug.Log($"OSC Receiver initialized: {localAddress}:{localPort}");
        }

        private void BindAvatarControls()
        {
            // Avatar loading and management
            bindBundle.Add($"{AVATAR_BASE}/load", AvatarLoad);
            bindBundle.Add($"{AVATAR_BASE}/unload", AvatarUnload);
            bindBundle.Add($"{AVATAR_BASE}/reset", AvatarReset);
            bindBundle.Add($"{AVATAR_BASE}/visibility", AvatarVisibility);

            // Transform controls
            bindBundle.Add($"{AVATAR_BASE}/position", AvatarPosition);
            bindBundle.Add($"{AVATAR_BASE}/rotation", AvatarRotation);
            bindBundle.Add($"{AVATAR_BASE}/scale", AvatarScale);
            bindBundle.Add($"{AVATAR_BASE}/lookat", AvatarLookAt);

            // Animation controls
            bindBundle.Add($"{AVATAR_BASE}/animation/play", AnimationPlay);
            bindBundle.Add($"{AVATAR_BASE}/animation/stop", AnimationStop);
            bindBundle.Add($"{AVATAR_BASE}/animation/stop_all", AnimationStopAll);
            bindBundle.Add($"{AVATAR_BASE}/animation/crossfade", AnimationCrossfade);
            bindBundle.Add($"{AVATAR_BASE}/animation/parameter", AnimationParameter);

            // Expression controls
            bindBundle.Add($"{AVATAR_BASE}/expression/set", ExpressionSet);
            bindBundle.Add($"{AVATAR_BASE}/expression/blendshape", ExpressionBlendShape);
            bindBundle.Add($"{AVATAR_BASE}/expression/reset", ExpressionReset);
            bindBundle.Add($"{AVATAR_BASE}/expression/eyebrow", ExpressionEyebrow);
            bindBundle.Add($"{AVATAR_BASE}/expression/eye", ExpressionEye);
            bindBundle.Add($"{AVATAR_BASE}/expression/mouth", ExpressionMouth);

            // Movement controls
            bindBundle.Add($"{AVATAR_BASE}/movement/walk", MovementWalk);
            bindBundle.Add($"{AVATAR_BASE}/movement/run", MovementRun);
            bindBundle.Add($"{AVATAR_BASE}/movement/turn", MovementTurn);
            bindBundle.Add($"{AVATAR_BASE}/movement/jump", MovementJump);
            bindBundle.Add($"{AVATAR_BASE}/movement/stop", MovementStop);

            // Gesture controls
            bindBundle.Add($"{AVATAR_BASE}/gesture/play", GesturePlay);
            bindBundle.Add($"{AVATAR_BASE}/gesture/stop", GestureStop);
        }

        private void BindWindowControls()
        {
            // Positioning
            bindBundle.Add($"{WINDOW_BASE}/position", WindowPosition);
            bindBundle.Add($"{WINDOW_BASE}/size", WindowSize);
            bindBundle.Add($"{WINDOW_BASE}/move", WindowMove);
            bindBundle.Add($"{WINDOW_BASE}/center", WindowCenter);
            bindBundle.Add($"{WINDOW_BASE}/monitor", WindowMonitor);

            // Appearance
            bindBundle.Add($"{WINDOW_BASE}/opacity", WindowOpacity);
            bindBundle.Add($"{WINDOW_BASE}/clickthrough", WindowClickThrough);
            bindBundle.Add($"{WINDOW_BASE}/alwaysontop", WindowAlwaysOnTop);
            bindBundle.Add($"{WINDOW_BASE}/visibility", WindowVisibility);
            bindBundle.Add($"{WINDOW_BASE}/border", WindowBorder);

            // State
            bindBundle.Add($"{WINDOW_BASE}/focus", WindowFocus);
            bindBundle.Add($"{WINDOW_BASE}/minimize", WindowMinimize);
            bindBundle.Add($"{WINDOW_BASE}/maximize", WindowMaximize);
            bindBundle.Add($"{WINDOW_BASE}/restore", WindowRestore);
            bindBundle.Add($"{WINDOW_BASE}/close", WindowClose);
        }

        private void BindSystemControls()
        {
            bindBundle.Add($"{SYSTEM_BASE}/status", SystemStatus);
            bindBundle.Add($"{SYSTEM_BASE}/version", SystemVersion);
            bindBundle.Add($"{SYSTEM_BASE}/restart", SystemRestart);
            bindBundle.Add($"{SYSTEM_BASE}/exit", SystemExit);
        }

        #endregion

        #region OSC Control Methods

        #region Avatar Controls

        private void AvatarLoad(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                string path = message.Values[0].StringValue;
                if (avatarController != null)
                {
                    avatarController.LoadAvatar(path);
                }
            }
        }

        private void AvatarUnload(extOSC.OSCPacket packet)
        {
            if (avatarController != null)
            {
                avatarController.UnloadAvatar();
            }
        }

        private void AvatarReset(extOSC.OSCPacket packet)
        {
            if (avatarController != null)
            {
                avatarController.ResetTransform();
            }
        }

        private void AvatarVisibility(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                bool visible = message.Values[0].BoolValue;
                if (avatarController != null)
                {
                    avatarController.SetVisibility(visible);
                }
            }
        }

        private void AvatarPosition(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 3)
            {
                Vector3 position = new Vector3(
                    message.Values[0].FloatValue,
                    message.Values[1].FloatValue,
                    message.Values[2].FloatValue
                );

                if (avatarController != null)
                {
                    avatarController.SetPosition(position);
                }
            }
        }

        private void AvatarRotation(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 3)
            {
                Vector3 eulerAngles = new Vector3(
                    message.Values[0].FloatValue,
                    message.Values[1].FloatValue,
                    message.Values[2].FloatValue
                );

                if (avatarController != null)
                {
                    avatarController.SetRotation(eulerAngles);
                }
            }
        }

        private void AvatarScale(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                float scale = message.Values[0].FloatValue;
                if (avatarController != null)
                {
                    avatarController.SetScale(scale);
                }
            }
        }

        private void AvatarLookAt(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 3)
            {
                Vector3 target = new Vector3(
                    message.Values[0].FloatValue,
                    message.Values[1].FloatValue,
                    message.Values[2].FloatValue
                );

                if (avatarController != null)
                {
                    avatarController.LookAt(target);
                }
            }
        }

        #endregion

        #region Animation Controls

        private void AnimationPlay(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 1)
            {
                string animationName = message.Values[0].StringValue;
                bool loop = message.Values.Count > 1 ? message.Values[1].BoolValue : false;
                float speed = message.Values.Count > 2 ? message.Values[2].FloatValue : 1.0f;

                if (avatarController != null)
                {
                    avatarController.PlayAnimation(animationName, loop, speed);
                }
            }
        }

        private void AnimationStop(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                string animationName = message.Values[0].StringValue;
                // Implementation would need to be added to AvatarController
            }
        }

        private void AnimationStopAll(extOSC.OSCPacket packet)
        {
            if (avatarController != null)
            {
                avatarController.StopAnimation();
            }
        }

        private void AnimationCrossfade(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 1)
            {
                string animationName = message.Values[0].StringValue;
                float duration = message.Values.Count > 1 ? message.Values[1].FloatValue : 0.3f;
                int layer = message.Values.Count > 2 ? message.Values[2].IntValue : 0;

                if (avatarController != null)
                {
                    avatarController.CrossfadeAnimation(animationName, duration, layer);
                }
            }
        }

        private void AnimationParameter(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                string parameterName = message.Values[0].StringValue;
                object value = message.Values[1].Value;

                if (avatarController != null)
                {
                    avatarController.SetAnimationParameter(parameterName, value);
                }
            }
        }

        #endregion

        #region Expression Controls

        private void ExpressionSet(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 1)
            {
                string presetName = message.Values[0].StringValue;
                float value = message.Values.Count > 1 ? message.Values[1].FloatValue : 1.0f;

                if (avatarController != null)
                {
                    avatarController.SetExpression(presetName, value);
                }
            }
        }

        private void ExpressionBlendShape(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                string blendShapeName = message.Values[0].StringValue;
                float value = message.Values[1].FloatValue;

                if (avatarController != null)
                {
                    avatarController.SetBlendShape(blendShapeName, value);
                }
            }
        }

        private void ExpressionReset(extOSC.OSCPacket packet)
        {
            if (avatarController != null)
            {
                avatarController.ResetExpressions();
            }
        }

        private void ExpressionEyebrow(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                float leftValue = message.Values[0].FloatValue;
                float rightValue = message.Values[1].FloatValue;

                if (avatarController != null)
                {
                    avatarController.SetEyebrows(leftValue, rightValue);
                }
            }
        }

        private void ExpressionEye(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                float leftValue = message.Values[0].FloatValue;
                float rightValue = message.Values[1].FloatValue;

                if (avatarController != null)
                {
                    avatarController.SetEyes(leftValue, rightValue);
                }
            }
        }

        private void ExpressionMouth(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                string shapeName = message.Values[0].StringValue;
                float value = message.Values[1].FloatValue;

                if (avatarController != null)
                {
                    avatarController.SetMouth(shapeName, value);
                }
            }
        }

        #endregion

        #region Movement Controls

        private void MovementWalk(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                // Implementation would require movement system
                float direction = message.Values[0].FloatValue;
                float speed = message.Values[1].FloatValue;
                Debug.Log($"Walk: direction={direction}, speed={speed}");
            }
        }

        private void MovementRun(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                float direction = message.Values[0].FloatValue;
                float speed = message.Values[1].FloatValue;
                Debug.Log($"Run: direction={direction}, speed={speed}");
            }
        }

        private void MovementTurn(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                float degrees = message.Values[0].FloatValue;
                float speed = message.Values[1].FloatValue;
                Debug.Log($"Turn: degrees={degrees}, speed={speed}");
            }
        }

        private void MovementJump(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                float height = message.Values[0].FloatValue;
                Debug.Log($"Jump: height={height}");
            }
        }

        private void MovementStop(extOSC.OSCPacket packet)
        {
            Debug.Log("Movement stopped");
        }

        #endregion

        #region Gesture Controls

        private void GesturePlay(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 1)
            {
                string gestureName = message.Values[0].StringValue;
                float intensity = message.Values.Count > 1 ? message.Values[1].FloatValue : 1.0f;
                Debug.Log($"Play gesture: {gestureName}, intensity={intensity}");
            }
        }

        private void GestureStop(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                string gestureName = message.Values[0].StringValue;
                Debug.Log($"Stop gesture: {gestureName}");
            }
        }

        #endregion

        #region Window Controls

        private void WindowPosition(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                int x = message.Values[0].IntValue;
                int y = message.Values[1].IntValue;

                if (windowManager != null)
                {
                    windowManager.SetPosition(x, y);
                }
            }
        }

        private void WindowSize(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                int width = message.Values[0].IntValue;
                int height = message.Values[1].IntValue;

                if (windowManager != null)
                {
                    windowManager.SetSize(width, height);
                }
            }
        }

        private void WindowMove(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count >= 2)
            {
                int dx = message.Values[0].IntValue;
                int dy = message.Values[1].IntValue;

                if (windowManager != null)
                {
                    windowManager.MoveRelative(dx, dy);
                }
            }
        }

        private void WindowCenter(extOSC.OSCPacket packet)
        {
            if (windowManager != null)
            {
                windowManager.CenterOnScreen();
            }
        }

        private void WindowMonitor(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                int monitorIndex = message.Values[0].IntValue;

                if (windowManager != null)
                {
                    windowManager.MoveToMonitor(monitorIndex);
                }
            }
        }

        private void WindowOpacity(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                float opacity = message.Values[0].FloatValue;

                if (windowManager != null)
                {
                    windowManager.SetTransparencyLevel(opacity);
                }
            }
        }

        private void WindowClickThrough(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                bool clickThrough = message.Values[0].BoolValue;

                if (windowManager != null)
                {
                    windowManager.SetClickThrough(clickThrough);
                }
            }
        }

        private void WindowAlwaysOnTop(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                bool alwaysOnTop = message.Values[0].BoolValue;

                if (windowManager != null)
                {
                    windowManager.SetAlwaysOnTop(alwaysOnTop);
                }
            }
        }

        private void WindowVisibility(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                bool visible = message.Values[0].BoolValue;

                if (windowManager != null)
                {
                    // Note: Window visibility is separate from avatar visibility
                    // This would need additional implementation
                }
            }
        }

        private void WindowBorder(extOSC.OSCPacket packet)
        {
            if (packet is extOSC.OSCMessage message && message.Values.Count > 0)
            {
                bool border = message.Values[0].BoolValue;

                if (windowManager != null)
                {
                    windowManager.SetBorderless(!border);
                }
            }
        }

        private void WindowFocus(extOSC.OSCPacket packet)
        {
            if (windowManager != null)
            {
                windowManager.BringToFront();
            }
        }

        private void WindowMinimize(extOSC.OSCPacket packet)
        {
            if (windowManager != null)
            {
                windowManager.Minimize();
            }
        }

        private void WindowMaximize(extOSC.OSCPacket packet)
        {
            if (windowManager != null)
            {
                windowManager.Maximize();
            }
        }

        private void WindowRestore(extOSC.OSCPacket packet)
        {
            if (windowManager != null)
            {
                windowManager.Restore();
            }
        }

        private void WindowClose(extOSC.OSCPacket packet)
        {
            if (windowManager != null)
            {
                windowManager.Close();
            }
        }

        #endregion

        #region System Controls

        private void SystemStatus(extOSC.OSCPacket packet)
        {
            // Send status information back
            // This would require an OSC sender component
            Debug.Log("System status requested");
        }

        private void SystemVersion(extOSC.OSCPacket packet)
        {
            Debug.Log($"Version: {Application.version}");
        }

        private void SystemRestart(extOSC.OSCPacket packet)
        {
            Debug.Log("System restart requested");
            // Implementation for restart
        }

        private void SystemExit(extOSC.OSCPacket packet)
        {
            Debug.Log("System exit requested");
            Application.Quit();
        }

        #endregion

        #region OSC Management

        /// <summary>
        /// Start OSC receiver
        /// </summary>
        public void StartOSC()
        {
            if (receiver != null)
            {
                receiver.Connect();
                Debug.Log("OSC Receiver started");
            }
        }

        /// <summary>
        /// Stop OSC receiver
        /// </summary>
        public void StopOSC()
        {
            if (receiver != null)
            {
                receiver.Close();
                Debug.Log("OSC Receiver stopped");
            }
        }

        /// <summary>
        /// Check if OSC receiver is connected
        /// </summary>
        public bool IsConnected()
        {
            return receiver != null && receiver.IsConnected;
        }

        /// <summary>
        /// Get OSC receiver status
        /// </summary>
        public string GetStatus()
        {
            if (receiver == null) return "Not initialized";

            return receiver.IsConnected ?
                $"Connected to {receiver.LocalHost}:{receiver.LocalPort}" :
                "Disconnected";
        }

        #endregion
    }
}
