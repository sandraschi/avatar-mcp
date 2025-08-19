using UnityEngine;
using VRM;
using System.Collections.Generic;
using System.Linq;

[RequireComponent(typeof(Animator))]
public class AvatarController : MonoBehaviour
{
    #region Public Fields

    [Header("Avatar Settings")]
    public float movementSpeed = 2.0f;
    public float rotationSpeed = 100.0f;
    public float jumpForce = 5.0f;
    public float gravity = 9.81f;

    [Header("References")]
    public Camera mainCamera;
    public Transform cameraTarget;
    public float cameraDistance = 2.0f;
    public Vector3 cameraOffset = new Vector3(0, 1.5f, 0);

    #endregion

    #region Private Fields

    private Animator _animator;
    private VRMBlendShapeProxy _blendShapeProxy;
    private CharacterController _characterController;
    private Vector3 _movement;
    private float _verticalVelocity;
    private bool _isGrounded;
    private Dictionary<string, float> _expressions = new Dictionary<string, float>();
    private Dictionary<string, float> _blendShapes = new Dictionary<string, float>();

    #endregion

    #region Unity Methods

    private void Awake()
    {
        _animator = GetComponent<Animator>();
        _blendShapeProxy = GetComponent<VRMBlendShapeProxy>();
        _characterController = GetComponent<CharacterController>();
        
        if (mainCamera == null)
            mainCamera = Camera.main;
            
        if (cameraTarget == null)
            cameraTarget = transform;
    }

    private void Start()
    {
        InitializeBlendShapes();
        InitializeExpressions();
        
        // Set up camera
        if (mainCamera != null)
        {
            mainCamera.transform.position = cameraTarget.position - (Vector3.forward * cameraDistance) + cameraOffset;
            mainCamera.transform.LookAt(cameraTarget.position + cameraOffset);
        }
    }

    private void Update()
    {
        HandleGravity();
        UpdateAnimator();
        UpdateCamera();
    }

    #endregion

    #region Public Methods - Movement

    public void Walk(string direction, float speed = 1.0f)
    {
        var moveDirection = GetDirectionVector(direction);
        _movement = moveDirection * (movementSpeed * speed);
        
        // Face movement direction
        if (moveDirection != Vector3.zero)
        {
            var targetRotation = Quaternion.LookRotation(moveDirection);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, Time.deltaTime * rotationSpeed);
        }
    }

    public void Run(string direction, float speed = 1.5f)
    {
        Walk(direction, speed * 1.5f);
    }

    public void Jump(float height = 1.0f)
    {
        if (_isGrounded)
        {
            _verticalVelocity = Mathf.Sqrt(jumpForce * height * -2f * -gravity);
            _animator.SetTrigger("Jump");
        }
    }

    public void Turn(float angle, float speed = 1.0f)
    {
        transform.Rotate(0, angle * speed * Time.deltaTime, 0);
    }

    public void StopMovement()
    {
        _movement = Vector3.zero;
    }

    #endregion

    #region Public Methods - Animation

    public void PlayAnimation(string animationName, bool loop = false, float speed = 1.0f)
    {
        if (_animator == null) return;
        
        _animator.speed = speed;
        
        if (loop)
        {
            _animator.Play(animationName, -1, 0f);
        }
        else
        {
            _animator.Play(animationName);
        }
    }

    public void PlayGesture(string gestureName, Dictionary<string, float> parameters = null)
    {
        // This would be implemented based on your specific gesture system
        // For example, triggering animation states or blend trees
        _animator.SetTrigger(gestureName);
        
        // Apply any additional parameters
        if (parameters != null)
        {
            foreach (var param in parameters)
            _animator.SetFloat(param.Key, param.Value);
        }
    }

    #endregion

    #region Public Methods - Expressions

    public void SetExpression(string name, float value)
    {
        if (_expressions.ContainsKey(name))
        {
            _expressions[name] = Mathf.Clamp01(value);
            UpdateBlendShapes();
        }
    }

    public void SetBlendShape(string name, float value)
    {
        if (_blendShapes.ContainsKey(name))
        {
            _blendShapes[name] = Mathf.Clamp01(value);
            UpdateBlendShapes();
        }
    }

    #endregion

    #region Public Methods - Transform

    public void SetPosition(Vector3 position)
    {
        if (_characterController != null)
            _characterController.Move(position - transform.position);
        else
            transform.position = position;
    }

    public void SetRotation(Quaternion rotation)
    {
        transform.rotation = rotation;
    }

    public void SetScale(float scale)
    {
        transform.localScale = Vector3.one * scale;
    }

    #endregion

    #region Private Methods

    private void InitializeBlendShapes()
    {
        if (_blendShapeProxy == null) return;
        
        var clips = _blendShapeProxy.BlendShapeAvatar.Clips;
        foreach (var clip in clips)
        {
            if (!_blendShapes.ContainsKey(clip.BlendShapeName))
                _blendShapes.Add(clip.BlendShapeName, 0f);
        }
    }

    private void InitializeExpressions()
    {
        // Add common expressions
        string[] expressions = { "Neutral", "Happy", "Sad", "Angry", "Surprised", "Blink", "Blink_L", "Blink_R" };
        
        foreach (var exp in expressions)
        {
            if (!_expressions.ContainsKey(exp))
                _expressions.Add(exp, 0f);
        }
    }

    private void UpdateBlendShapes()
    {
        if (_blendShapeProxy == null) return;
        
        var values = new Dictionary<BlendShapeKey, float>();
        
        // Update expressions
        foreach (var exp in _expressions)
        {
            if (exp.Value > 0)
                values[BlendShapeKey.CreateFromPreset(GetBlendShapePreset(exp.Key))] = exp.Value;
        }
        
        // Update blend shapes
        foreach (var shape in _blendShapes)
        {
            if (shape.Value > 0)
                values[BlendShapeKey.CreateUnknown(shape.Key)] = shape.Value;
        }
        
        _blendShapeProxy.SetValues(values);
    }

    private BlendShapePreset GetBlendShapePreset(string name)
    {
        if (System.Enum.TryParse<BlendShapePreset>(name, out var preset))
            return preset;
            
        return BlendShapePreset.Unknown;
    }

    private void HandleGravity()
    {
        if (_characterController == null) return;
        
        _isGrounded = _characterController.isGrounded;
        
        if (_isGrounded && _verticalVelocity < 0)
            _verticalVelocity = -2f;
            
        _verticalVelocity += -gravity * Time.deltaTime;
        
        var move = _movement + new Vector3(0, _verticalVelocity, 0);
        _characterController.Move(move * Time.deltaTime);
    }

    private void UpdateAnimator()
    {
        if (_animator == null) return;
        
        // Convert movement to local space for animation
        var localMovement = transform.InverseTransformDirection(_movement);
        
        _animator.SetFloat("Forward", localMovement.z);
        _animator.SetFloat("Strafe", localMovement.x);
        _animator.SetBool("IsGrounded", _isGrounded);
        _animator.SetFloat("VerticalVelocity", _verticalVelocity);
    }

    private void UpdateCamera()
    {
        if (mainCamera == null || cameraTarget == null) return;
        
        var targetPosition = cameraTarget.position + cameraOffset - (mainCamera.transform.forward * cameraDistance);
        mainCamera.transform.position = Vector3.Lerp(mainCamera.transform.position, targetPosition, Time.deltaTime * 5f);
        mainCamera.transform.LookAt(cameraTarget.position + cameraOffset);
    }

    private Vector3 GetDirectionVector(string direction)
    {
        return direction.ToLower() switch
        {
            "forward" => transform.forward,
            "back" or "backward" => -transform.forward,
            "right" => transform.right,
            "left" => -transform.right,
            _ => transform.forward
        };
    }

    #endregion
}
