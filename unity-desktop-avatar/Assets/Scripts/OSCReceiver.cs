using UnityEngine;
using System;
using System.Collections.Generic;
using ExtOSC;

[RequireComponent(typeof(AvatarController))]
public class OSCReceiver : MonoBehaviour
{
    #region Public Fields

    [Header("OSC Settings")]
    public int port = 9000;
    public string addressPrefix = "/avatar";

    [Header("Debug")]
    public bool debugLog = false;

    #endregion

    #region Private Fields

    private OSCReceiver _receiver;
    private AvatarController _avatarController;
    private Dictionary<string, Action<OSCMessage>> _handlers;

    #endregion

    #region Unity Methods

    private void Awake()
    {
        _avatarController = GetComponent<AvatarController>();
        InitializeHandlers();
    }

    private void Start()
    {
        _receiver = gameObject.AddComponent<OSCEventReceiver>();
        (_receiver as OSCEventReceiver).localPort = port;
        (_receiver as OSCEventReceiver).BindAll(OnOSCMessageReceived);
        
        if (debugLog)
            Debug.Log($"[OSC] Listening on port {port}");
    }

    private void OnDestroy()
    {
        if (_receiver != null)
            Destroy(_receiver);
    }

    #endregion

    #region Private Methods

    private void InitializeHandlers()
    {
        _handlers = new Dictionary<string, Action<OSCMessage>>
        {
            { "expression", HandleExpression },
            { "gesture", HandleGesture },
            { "position", HandlePosition },
            { "scale", HandleScale },
            { "rotation", HandleRotation },
            { "blendshape", HandleBlendShape },
            { "animation", HandleAnimation },
            { "movement", HandleMovement }
        };
    }

    private void OnOSCMessageReceived(OSCMessage message)
    {
        try
        {
            if (message == null || message.Address == null)
                return;

            // Remove the address prefix and split the remaining path
            var path = message.Address.ToString().Substring(addressPrefix.Length).TrimStart('/');
            var parts = path.Split('/');

            if (parts.Length == 0)
                return;

            var handlerKey = parts[0].ToLower();
            if (_handlers.TryGetValue(handlerKey, out var handler))
            {
                handler.Invoke(message);
            }
            else if (debugLog)
            {
                Debug.Log($"[OSC] No handler for: {path}");
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[OSC] Error processing message: {e.Message}");
        }
    }

    #endregion

    #region Message Handlers

    private void HandleExpression(OSCMessage message)
    {
        if (message.Values.Count < 2) return;
        
        var name = message.Values[0].StringValue;
        var value = (float)message.Values[1].NumericValue();
        
        _avatarController.SetExpression(name, value);
        
        if (debugLog)
            Debug.Log($"[OSC] Set expression '{name}' to {value}");
    }

    private void HandleGesture(OSCMessage message)
    {
        if (message.Values.Count == 0) return;
        
        var gestureName = message.Values[0].StringValue;
        var parameters = new Dictionary<string, float>();
        
        // Parse additional parameters if any
        for (int i = 1; i < message.Values.Count; i += 2)
        {
            if (i + 1 >= message.Values.Count) break;
            parameters[message.Values[i].StringValue] = (float)message.Values[i + 1].NumericValue();
        }
        
        _avatarController.PlayGesture(gestureName, parameters);
        
        if (debugLog)
            Debug.Log($"[OSC] Played gesture: {gestureName}");
    }

    private void HandlePosition(OSCMessage message)
    {
        if (message.Values.Count < 3) return;
        
        var x = (float)message.Values[0].NumericValue();
        var y = (float)message.Values[1].NumericValue();
        var z = (float)message.Values[2].NumericValue();
        
        _avatarController.SetPosition(new Vector3(x, y, z));
    }

    private void HandleScale(OSCMessage message)
    {
        if (message.Values.Count < 1) return;
        
        var scale = (float)message.Values[0].NumericValue();
        _avatarController.SetScale(scale);
    }

    private void HandleRotation(OSCMessage message)
    {
        if (message.Values.Count < 4) return;
        
        var x = (float)message.Values[0].NumericValue();
        var y = (float)message.Values[1].NumericValue();
        var z = (float)message.Values[2].NumericValue();
        var w = (float)message.Values[3].NumericValue();
        
        _avatarController.SetRotation(new Quaternion(x, y, z, w));
    }

    private void HandleBlendShape(OSCMessage message)
    {
        if (message.Values.Count < 2) return;
        
        var name = message.Values[0].StringValue;
        var value = (float)message.Values[1].NumericValue();
        
        _avatarController.SetBlendShape(name, value);
    }

    private void HandleAnimation(OSCMessage message)
    {
        if (message.Values.Count < 1) return;
        
        var animationName = message.Values[0].StringValue;
        var loop = message.Values.Count > 1 ? message.Values[1].BoolValue : false;
        var speed = message.Values.Count > 2 ? (float)message.Values[2].NumericValue() : 1.0f;
        
        _avatarController.PlayAnimation(animationName, loop, speed);
    }

    private void HandleMovement(OSCMessage message)
    {
        if (message.Values.Count < 1) return;
        
        var movementType = message.Values[0].StringValue.ToLower();
        
        switch (movementType)
        {
            case "walk":
                var direction = message.Values.Count > 1 ? message.Values[1].StringValue : "forward";
                var speed = message.Values.Count > 2 ? (float)message.Values[2].NumericValue() : 1.0f;
                _avatarController.Walk(direction, speed);
                break;
                
            case "run":
                direction = message.Values.Count > 1 ? message.Values[1].StringValue : "forward";
                speed = message.Values.Count > 2 ? (float)message.Values[2].NumericValue() : 1.5f;
                _avatarController.Run(direction, speed);
                break;
                
            case "jump":
                var height = message.Values.Count > 1 ? (float)message.Values[1].NumericValue() : 1.0f;
                _avatarController.Jump(height);
                break;
                
            case "turn":
                var angle = message.Values.Count > 1 ? (float)message.Values[1].NumericValue() : 90f;
                var turnSpeed = message.Values.Count > 2 ? (float)message.Values[2].NumericValue() : 1.0f;
                _avatarController.Turn(angle, turnSpeed);
                break;
                
            case "stop":
                _avatarController.StopMovement();
                break;
        }
    }

    #endregion
}
