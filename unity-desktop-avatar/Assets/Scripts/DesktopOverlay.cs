using UnityEngine;
using UnityEngine.UI;
using System.IO;
using VRM;

public class DesktopOverlay : MonoBehaviour
{
    #region Public Fields

    [Header("UI References")]
    public Button loadAvatarButton;
    public InputField vrmPathInput;
    public Slider scaleSlider;
    public Toggle clickThroughToggle;
    public Toggle alwaysOnTopToggle;
    public Text statusText;

    [Header("Settings")]
    public string defaultVrmPath = "";
    public float defaultScale = 1.0f;
    public bool startWithClickThrough = false;
    public bool startAlwaysOnTop = true;

    [Header("References")]
    public GameObject avatarContainer;
    public Camera overlayCamera;
    public Light directionalLight;

    #endregion

    #region Private Fields

    private GameObject _currentAvatar;
    private WindowManager _windowManager;
    private OSCReceiver _oscReceiver;

    #endregion

    #region Unity Methods

    private void Awake()
    {
        _windowManager = GetComponent<WindowManager>();
        _oscReceiver = GetComponent<OSCReceiver>();
        
        // Initialize UI
        if (vrmPathInput != null)
            vrmPathInput.text = string.IsNullOrEmpty(defaultVrmPath) ? 
                Path.Combine(Application.streamingAssetsPath, "Avatars") : 
                defaultVrmPath;

        if (scaleSlider != null)
            scaleSlider.value = defaultScale;

        if (clickThroughToggle != null)
            clickThroughToggle.isOn = startWithClickThrough;

        if (alwaysOnTopToggle != null)
            alwaysOnTopToggle.isOn = startAlwaysOnTop;

        // Set initial window settings
        if (_windowManager != null)
        {
            _windowManager.clickThrough = startWithClickThrough;
            _windowManager.alwaysOnTop = startAlwaysOnTop;
        }
    }

    private void Start()
    {
        // Set up button callbacks
        if (loadAvatarButton != null)
            loadAvatarButton.onClick.AddListener(LoadAvatar);

        if (scaleSlider != null)
            scaleSlider.onValueChanged.AddListener(OnScaleChanged);

        if (clickThroughToggle != null)
            clickThroughToggle.onValueChanged.AddListener(OnClickThroughChanged);

        if (alwaysOnTopToggle != null)
            alwaysOnTopToggle.onValueChanged.AddListener(OnAlwaysOnTopChanged);

        // Initial status
        UpdateStatus("Ready. Load a VRM file to begin.");
    }

    #endregion

    #region Public Methods

    public async void LoadAvatar()
    {
        string path = vrmPathInput?.text ?? "";
        
        if (string.IsNullOrEmpty(path) || !File.Exists(path))
        {
            UpdateStatus($"File not found: {path}", true);
            return;
        }

        UpdateStatus("Loading VRM...");
        
        try
        {
            // Unload current avatar if exists
            if (_currentAvatar != null)
                Destroy(_currentAvatar);

            // Load VRM
            var bytes = File.ReadAllBytes(path);
            var context = new VRMImporterContext();
            context.ParseGlb(bytes);
            await context.LoadAsync();
            context.ShowMeshes();
            
            // Instantiate the avatar
            _currentAvatar = context.Root;
            _currentAvatar.transform.SetParent(avatarContainer.transform, false);
            
            // Set up the avatar
            var animator = _currentAvatar.GetComponent<Animator>();
            if (animator == null)
                animator = _currentAvatar.AddComponent<Animator>();
            
            // Add required components if they don't exist
            if (_currentAvatar.GetComponent<VRMBlendShapeProxy>() == null)
                _currentAvatar.AddComponent<VRMBlendShapeProxy>();
                
            if (_currentAvatar.GetComponent<VRMFirstPerson>() == null)
                _currentAvatar.AddComponent<VRMFirstPerson>();
                
            // Set up character controller if not present
            var controller = _currentAvatar.GetComponent<CharacterController>();
            if (controller == null)
            {
                controller = _currentAvatar.AddComponent<CharacterController>();
                controller.center = new Vector3(0, 0.9f, 0);
                controller.radius = 0.3f;
                controller.height = 1.7f;
            }
            
            // Initialize the avatar controller
            var avatarController = _currentAvatar.GetComponent<AvatarController>();
            if (avatarController == null)
                avatarController = _currentAvatar.AddComponent<AvatarController>();
                
            // Set up camera target
            var headBone = animator.GetBoneTransform(HumanBodyBones.Head);
            if (headBone != null)
            {
                if (avatarController.cameraTarget == null)
                {
                    var targetObj = new GameObject("CameraTarget");
                    targetObj.transform.SetParent(headBone);
                    targetObj.transform.localPosition = Vector3.zero;
                    avatarController.cameraTarget = targetObj.transform;
                }
            }
            
            // Apply scale
            OnScaleChanged(scaleSlider != null ? scaleSlider.value : defaultScale);
            
            UpdateStatus($"Loaded: {Path.GetFileName(path)}");
        }
        catch (System.Exception e)
        {
            UpdateStatus($"Error loading VRM: {e.Message}", true);
            Debug.LogException(e);
            
            if (_currentAvatar != null)
            {
                Destroy(_currentAvatar);
                _currentAvatar = null;
            }
        }
    }

    public void UpdateStatus(string message, bool isError = false)
    {
        if (statusText != null)
        {
            statusText.text = message;
            statusText.color = isError ? Color.red : Color.white;
        }
        
        Debug.Log($"[Status] {message}");
    }

    #endregion

    #region UI Callbacks

    private void OnScaleChanged(float value)
    {
        if (_currentAvatar != null)
            _currentAvatar.transform.localScale = Vector3.one * value;
    }

    private void OnClickThroughChanged(bool value)
    {
        if (_windowManager != null)
            _windowManager.clickThrough = value;
    }

    private void OnAlwaysOnTopChanged(bool value)
    {
        if (_windowManager != null)
            _windowManager.alwaysOnTop = value;
    }

    #endregion
}
