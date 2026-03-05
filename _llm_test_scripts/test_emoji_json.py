import json

# Test JSON serialization with emojis
test_response = {
    'success': False,
    'message': "I'd love to help you create an avatar workflow, but I need you to tell me what you'd like the avatar to do! 😊",
    'suggestion': "Try describing something like 'Express happiness with a smile and wave'",
    'example': "workflow_prompt: 'Create a warm welcome with a friendly smile and gentle wave'"
}

try:
    json_str = json.dumps(test_response, ensure_ascii=False)
    print('SUCCESS: JSON serialization with emojis works perfectly')
    print(f'Length: {len(json_str)} characters')

    # Test deserialization
    parsed = json.loads(json_str)
    print('SUCCESS: JSON deserialization also works')
    print('Emoji preserved:', repr(parsed['message'][-2:]))

except Exception as e:
    print(f'ERROR: JSON serialization failed: {e}')