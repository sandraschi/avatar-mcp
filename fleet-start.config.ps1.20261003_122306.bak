# Per-repo fleet start config for avatar-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'avatar-mcp'
    BackendPort  = 10793
    FrontendPort = 10792
    HealthPath   = '/api/v1/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'avatarmcp.http_server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10793' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
