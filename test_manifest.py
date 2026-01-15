import json

try:
    with open('mcpb/manifest_portmanteau.json', 'r') as f:
        manifest = json.load(f)

    print('SUCCESS: Manifest loads successfully')
    print(f'Version: {manifest["version"]}')
    print(f'Tools: {len(manifest["tools"])}')
    print(f'Prompts: {len(manifest["prompts"])}')

    # Check for sampling tool
    sampling_tool = any(tool['name'] == 'avatar_sampling' for tool in manifest['tools'])
    if sampling_tool:
        print('SUCCESS: avatar_sampling tool found')
    else:
        print('ERROR: avatar_sampling tool not found')

    # Check for sampling prompts
    sampling_prompts = [p for p in manifest['prompts'] if 'sampling' in p['name'].lower()]
    print(f'Sampling prompts: {len(sampling_prompts)}')

except Exception as e:
    print(f'ERROR: {e}')