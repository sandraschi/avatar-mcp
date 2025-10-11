using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using UniGLTF;
using VRM;

namespace AvatarMCP.VRM
{
    /// <summary>
    /// Handles loading and management of VRM avatars
    /// </summary>
    public class VRMLoader : MonoBehaviour
    {
        [Header("VRM Loading Settings")]
        [SerializeField] private string defaultAvatarPath = "StreamingAssets/Avatars/default.vrm";
        [SerializeField] private bool autoLoadDefault = true;
        [SerializeField] private float defaultScale = 1.0f;
        [SerializeField] private Vector3 defaultPosition = Vector3.zero;

        // Events
        public event Action<GameObject> OnAvatarLoaded;
        public event Action<string> OnAvatarLoadFailed;
        public event Action<GameObject> OnAvatarUnloaded;

        // Current avatar
        private GameObject currentAvatar;
        private VRMImporterContext currentContext;
        private VRMBlendShapeProxy blendShapeProxy;
        private Animator animator;

        private void Start()
        {
            if (autoLoadDefault && !string.IsNullOrEmpty(defaultAvatarPath))
            {
                LoadAvatarAsync(defaultAvatarPath);
            }
        }

        private void OnDestroy()
        {
            UnloadCurrentAvatar();
        }

        /// <summary>
        /// Load a VRM avatar from file path
        /// </summary>
        public async void LoadAvatarAsync(string filePath)
        {
            try
            {
                Debug.Log($"Loading VRM avatar: {filePath}");

                // Unload current avatar first
                UnloadCurrentAvatar();

                // Load VRM file
                var context = await LoadVRMContextAsync(filePath);
                if (context == null)
                {
                    OnAvatarLoadFailed?.Invoke($"Failed to load VRM context: {filePath}");
                    return;
                }

                // Show avatar in scene
                var avatar = context.ShowMeshes();
                avatar.transform.SetParent(transform);
                avatar.transform.localPosition = defaultPosition;
                avatar.transform.localScale = Vector3.one * defaultScale;

                // Setup components
                SetupAvatarComponents(avatar, context);

                currentAvatar = avatar;
                currentContext = context;

                Debug.Log($"VRM avatar loaded successfully: {filePath}");
                OnAvatarLoaded?.Invoke(avatar);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load VRM avatar: {ex.Message}");
                OnAvatarLoadFailed?.Invoke(ex.Message);
            }
        }

        /// <summary>
        /// Unload the current avatar
        /// </summary>
        public void UnloadCurrentAvatar()
        {
            if (currentAvatar != null)
            {
                OnAvatarUnloaded?.Invoke(currentAvatar);
                Destroy(currentAvatar);
                currentAvatar = null;
            }

            if (currentContext != null)
            {
                currentContext.Dispose();
                currentContext = null;
            }

            blendShapeProxy = null;
            animator = null;
        }

        /// <summary>
        /// Get the current avatar GameObject
        /// </summary>
        public GameObject GetCurrentAvatar()
        {
            return currentAvatar;
        }

        /// <summary>
        /// Get the VRM blend shape proxy for facial expressions
        /// </summary>
        public VRMBlendShapeProxy GetBlendShapeProxy()
        {
            return blendShapeProxy;
        }

        /// <summary>
        /// Get the avatar animator for animations
        /// </summary>
        public Animator GetAnimator()
        {
            return animator;
        }

        private async Task<VRMImporterContext> LoadVRMContextAsync(string filePath)
        {
            // Handle different path formats
            string fullPath = GetFullPath(filePath);

            if (!File.Exists(fullPath))
            {
                throw new FileNotFoundException($"VRM file not found: {fullPath}");
            }

            // Load file bytes
            byte[] bytes = await LoadFileBytesAsync(fullPath);

            // Parse VRM
            var context = new VRMImporterContext();
            var parser = new GltfParser();
            parser.ParseGltf(bytes, new VRMImporterContext());

            // Import VRM
            var importer = new VRMImporter(parser, context);
            await importer.LoadAsync();

            return context;
        }

        private async Task<byte[]> LoadFileBytesAsync(string filePath)
        {
            using (var www = UnityWebRequest.Get(filePath))
            {
                var operation = www.SendWebRequest();

                while (!operation.isDone)
                {
                    await Task.Yield();
                }

                if (www.result != UnityWebRequest.Result.Success)
                {
                    throw new Exception($"Failed to load file: {www.error}");
                }

                return www.downloadHandler.data;
            }
        }

        private void SetupAvatarComponents(GameObject avatar, VRMImporterContext context)
        {
            // Get blend shape proxy for facial expressions
            blendShapeProxy = avatar.GetComponent<VRMBlendShapeProxy>();

            // Get animator for animations
            animator = avatar.GetComponent<Animator>();

            // Setup VRM components
            var vrmMeta = avatar.GetComponent<VRMMeta>();
            if (vrmMeta != null)
            {
                Debug.Log($"Loaded VRM: {vrmMeta.Meta.Title}");
            }

            // Setup first person (hide head for first person view if needed)
            var firstPerson = avatar.GetComponent<VRMFirstPerson>();
            if (firstPerson != null)
            {
                // Configure first person settings
            }

            // Setup look-at for head tracking
            var lookAt = avatar.GetComponent<VRMLookAt>();
            if (lookAt != null)
            {
                // Configure look-at settings
            }
        }

        private string GetFullPath(string filePath)
        {
            // Handle different path formats
            if (Path.IsPathRooted(filePath))
            {
                return filePath;
            }

            // Check StreamingAssets first
            string streamingPath = Path.Combine(Application.streamingAssetsPath, filePath);
            if (File.Exists(streamingPath))
            {
                return streamingPath;
            }

            // Check absolute path
            if (File.Exists(filePath))
            {
                return filePath;
            }

            // Check data path
            string dataPath = Path.Combine(Application.dataPath, filePath);
            if (File.Exists(dataPath))
            {
                return dataPath;
            }

            throw new FileNotFoundException($"VRM file not found in any expected location: {filePath}");
        }
    }
}
