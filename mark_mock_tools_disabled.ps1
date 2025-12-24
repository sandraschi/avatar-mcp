# PowerShell script to mark mock tools as disabled in manifest.json

$manifestPath = "mcpb/manifest.json"
$content = Get-Content $manifestPath -Raw

# List of mock tools to mark as disabled
$mockTools = @(
    "osc_receive",
    "chat_start", 
    "chat_send_message",
    "chat_stop",
    "chat_get_state",
    "system_status",
    "unity_system_status",
    "unity_window_position",
    "unity_window_transparency", 
    "unity_window_visibility",
    "unity_window_mode",
    "unity_avatar_load",
    "unity_avatar_expression",
    "unity_avatar_animation",
    "unity_osc_bridge",
    "unity_plugin_load",
    "unity_config_update"
)

foreach ($tool in $mockTools) {
    # Pattern to match the tool entry and add disabled fields
    $pattern = "(\s*\{\s*`"name`":\s*`"$tool`",\s*`"description`":\s*`"[^`"]*`")\s*\},"
    $replacement = "`$1,`n      `"disabled`": true,`n      `"disabled_reason`": `"Mock implementation - will be implemented in next release`"`n    },"
    
    $content = $content -replace $pattern, $replacement
}

# Write the updated content back
Set-Content $manifestPath $content -NoNewline

Write-Host "Marked $($mockTools.Count) mock tools as disabled in manifest.json"



