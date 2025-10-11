using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using VRM;

namespace AvatarMCP.VRM
{
    /// <summary>
    /// Main controller for avatar management and operations
    /// </summary>
    public class AvatarController : MonoBehaviour
    {
        [Header("Avatar Settings")]
        [SerializeField] private VRMLoader vrmLoader;
        [SerializeField] private Transform avatarRoot;
        [SerializeField] private float defaultScale = 1.0f;
        [SerializeField] private Vector3 defaultPosition = Vector3.zero;
        [SerializeField] private Vector3 defaultRotation = Vector3.zero;

        // Avatar state
        private GameObject currentAvatar;
        private VRMBlendShapeProxy blendShapeProxy;
        private Animator animator;
        private bool isVisible = true;

        // Events
        public event Action<GameObject> OnAvatarLoaded;
        public event Action<GameObject> OnAvatarUnloaded;
        public event Action OnAvatarVisibilityChanged;

        private void Awake()
        {
            if (vrmLoader == null)
            {
                vrmLoader = GetComponent<VRMLoader>();
            }

            if (avatarRoot == null)
            {
                avatarRoot = transform;
            }

            // Subscribe to VRM loader events
            if (vrmLoader != null)
            {
                vrmLoader.OnAvatarLoaded += OnVRMLoaded;
                vrmLoader.OnAvatarUnloaded += OnVRMUnloaded;
                vrmLoader.OnAvatarLoadFailed += OnVRMLoadFailed;
            }
        }

        private void OnDestroy()
        {
            // Unsubscribe from events
            if (vrmLoader != null)
            {
                vrmLoader.OnAvatarLoaded -= OnVRMLoaded;
                vrmLoader.OnAvatarUnloaded -= OnVRMUnloaded;
                vrmLoader.OnAvatarLoadFailed -= OnVRMLoadFailed;
            }
        }

        #region Avatar Management

        /// <summary>
        /// Load an avatar from file path
        /// </summary>
        public void LoadAvatar(string filePath)
        {
            if (vrmLoader != null)
            {
                vrmLoader.LoadAvatarAsync(filePath);
            }
        }

        /// <summary>
        /// Unload the current avatar
        /// </summary>
        public void UnloadAvatar()
        {
            if (vrmLoader != null)
            {
                vrmLoader.UnloadCurrentAvatar();
            }
        }

        /// <summary>
        /// Get the current avatar GameObject
        /// </summary>
        public GameObject GetCurrentAvatar()
        {
            return currentAvatar;
        }

        /// <summary>
        /// Check if an avatar is currently loaded
        /// </summary>
        public bool HasAvatar()
        {
            return currentAvatar != null;
        }

        #endregion

        #region Transform Control

        /// <summary>
        /// Set avatar position
        /// </summary>
        public void SetPosition(Vector3 position)
        {
            if (currentAvatar != null)
            {
                currentAvatar.transform.localPosition = position;
            }
        }

        /// <summary>
        /// Set avatar rotation
        /// </summary>
        public void SetRotation(Quaternion rotation)
        {
            if (currentAvatar != null)
            {
                currentAvatar.transform.localRotation = rotation;
            }
        }

        /// <summary>
        /// Set avatar rotation with Euler angles
        /// </summary>
        public void SetRotation(Vector3 eulerAngles)
        {
            SetRotation(Quaternion.Euler(eulerAngles));
        }

        /// <summary>
        /// Set avatar scale
        /// </summary>
        public void SetScale(float scale)
        {
            if (currentAvatar != null)
            {
                currentAvatar.transform.localScale = Vector3.one * scale;
            }
        }

        /// <summary>
        /// Set avatar scale with Vector3
        /// </summary>
        public void SetScale(Vector3 scale)
        {
            if (currentAvatar != null)
            {
                currentAvatar.transform.localScale = scale;
            }
        }

        /// <summary>
        /// Reset avatar to default transform
        /// </summary>
        public void ResetTransform()
        {
            SetPosition(defaultPosition);
            SetRotation(defaultRotation);
            SetScale(defaultScale);
        }

        /// <summary>
        /// Make avatar look at a point
        /// </summary>
        public void LookAt(Vector3 target)
        {
            if (currentAvatar != null)
            {
                currentAvatar.transform.LookAt(target);
            }
        }

        #endregion

        #region Visibility Control

        /// <summary>
        /// Set avatar visibility
        /// </summary>
        public void SetVisibility(bool visible)
        {
            if (isVisible != visible)
            {
                isVisible = visible;

                if (currentAvatar != null)
                {
                    var renderers = currentAvatar.GetComponentsInChildren<Renderer>();
                    foreach (var renderer in renderers)
                    {
                        renderer.enabled = visible;
                    }
                }

                OnAvatarVisibilityChanged?.Invoke();
            }
        }

        /// <summary>
        /// Toggle avatar visibility
        /// </summary>
        public void ToggleVisibility()
        {
            SetVisibility(!isVisible);
        }

        /// <summary>
        /// Get current avatar visibility
        /// </summary>
        public bool GetVisibility()
        {
            return isVisible;
        }

        #endregion

        #region Animation Control

        /// <summary>
        /// Play an animation by name
        /// </summary>
        public void PlayAnimation(string animationName, bool loop = false, float speed = 1.0f)
        {
            if (animator != null)
            {
                var clip = Resources.Load<AnimationClip>(animationName);
                if (clip != null)
                {
                    // Create animation state
                    var state = animator.GetCurrentAnimatorStateInfo(0);
                    animator.speed = speed;

                    // Play animation
                    animator.Play(animationName);

                    // Handle looping
                    if (!loop)
                    {
                        StartCoroutine(StopAnimationAfterClip(animationName, clip.length / speed));
                    }
                }
                else
                {
                    Debug.LogWarning($"Animation clip not found: {animationName}");
                }
            }
        }

        /// <summary>
        /// Stop current animation
        /// </summary>
        public void StopAnimation()
        {
            if (animator != null)
            {
                animator.StopPlayback();
            }
        }

        /// <summary>
        /// Crossfade to a new animation
        /// </summary>
        public void CrossfadeAnimation(string animationName, float duration = 0.3f, int layer = 0)
        {
            if (animator != null)
            {
                animator.CrossFadeInFixedTime(animationName, duration, layer);
            }
        }

        /// <summary>
        /// Set animation parameter
        /// </summary>
        public void SetAnimationParameter(string parameterName, object value)
        {
            if (animator != null)
            {
                if (value is bool boolValue)
                {
                    animator.SetBool(parameterName, boolValue);
                }
                else if (value is int intValue)
                {
                    animator.SetInteger(parameterName, intValue);
                }
                else if (value is float floatValue)
                {
                    animator.SetFloat(parameterName, floatValue);
                }
                else if (value is string triggerName)
                {
                    animator.SetTrigger(triggerName);
                }
            }
        }

        private IEnumerator StopAnimationAfterClip(string animationName, float duration)
        {
            yield return new WaitForSeconds(duration);
            if (animator != null && animator.GetCurrentAnimatorClipInfo(0).Length > 0)
            {
                var currentClip = animator.GetCurrentAnimatorClipInfo(0)[0].clip;
                if (currentClip != null && currentClip.name == animationName)
                {
                    StopAnimation();
                }
            }
        }

        #endregion

        #region Expression Control

        /// <summary>
        /// Set facial expression using blend shapes
        /// </summary>
        public void SetExpression(string presetName, float value = 1.0f)
        {
            if (blendShapeProxy != null)
            {
                var preset = GetBlendShapePreset(presetName);
                if (preset != null)
                {
                    blendShapeProxy.AccumulateValue(preset, value);
                    blendShapeProxy.Apply();
                }
            }
        }

        /// <summary>
        /// Set blend shape value directly
        /// </summary>
        public void SetBlendShape(string blendShapeName, float value)
        {
            if (blendShapeProxy != null)
            {
                var blendShape = GetBlendShapeKey(blendShapeName);
                if (blendShape != null)
                {
                    blendShapeProxy.AccumulateValue(blendShape, value);
                    blendShapeProxy.Apply();
                }
            }
        }

        /// <summary>
        /// Reset all facial expressions
        /// </summary>
        public void ResetExpressions()
        {
            if (blendShapeProxy != null)
            {
                blendShapeProxy.Reset();
            }
        }

        /// <summary>
        /// Set eyebrow position
        /// </summary>
        public void SetEyebrows(float leftValue, float rightValue)
        {
            SetBlendShape("EyebrowLeft", leftValue);
            SetBlendShape("EyebrowRight", rightValue);
        }

        /// <summary>
        /// Set eye openness
        /// </summary>
        public void SetEyes(float leftValue, float rightValue)
        {
            SetBlendShape("EyeLeft", leftValue);
            SetBlendShape("EyeRight", rightValue);
        }

        /// <summary>
        /// Set mouth shape
        /// </summary>
        public void SetMouth(string shapeName, float value)
        {
            SetBlendShape($"Mouth{shapeName}", value);
        }

        private BlendShapeKey GetBlendShapeKey(string name)
        {
            // Convert string name to BlendShapeKey
            // This would need to be implemented based on VRM specification
            return new BlendShapeKey(name);
        }

        private BlendShapePreset GetBlendShapePreset(string name)
        {
            // Convert preset name to BlendShapePreset enum
            switch (name.ToLower())
            {
                case "happy": return BlendShapePreset.Happy;
                case "angry": return BlendShapePreset.Angry;
                case "sad": return BlendShapePreset.Sad;
                case "relaxed": return BlendShapePreset.Relaxed;
                case "surprised": return BlendShapePreset.Surprised;
                case "blink": return BlendShapePreset.Blink;
                case "blink_l": return BlendShapePreset.Blink_L;
                case "blink_r": return BlendShapePreset.Blink_R;
                default: return BlendShapePreset.Unknown;
            }
        }

        #endregion

        #region Event Handlers

        private void OnVRMLoaded(GameObject avatar)
        {
            currentAvatar = avatar;
            blendShapeProxy = vrmLoader.GetBlendShapeProxy();
            animator = vrmLoader.GetAnimator();

            // Reset to default state
            ResetTransform();
            SetVisibility(true);
            ResetExpressions();

            OnAvatarLoaded?.Invoke(avatar);
        }

        private void OnVRMUnloaded(GameObject avatar)
        {
            currentAvatar = null;
            blendShapeProxy = null;
            animator = null;

            OnAvatarUnloaded?.Invoke(avatar);
        }

        private void OnVRMLoadFailed(string error)
        {
            Debug.LogError($"Avatar load failed: {error}");
        }

        #endregion
    }
}
